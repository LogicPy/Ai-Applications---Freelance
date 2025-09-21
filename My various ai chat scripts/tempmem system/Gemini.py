import asyncio
import os
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime, time, timedelta
import pytz
from typing import List, Dict, Any, Callable, Optional
import json
import re
import krakenex
import aiohttp  # For timeout handling

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
KRAKEN_API_KEY = os.getenv("KRAKEN_API_KEY")
KRAKEN_API_SECRET = os.getenv("KRAKEN_API_SECRET")

if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not found in .env file! 😅")
    exit(1)
if not KRAKEN_API_KEY or not KRAKEN_API_SECRET:
    print("Warning: Kraken API credentials not found. Trading disabled. 😅")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Kraken API client
k = None
if KRAKEN_API_KEY and KRAKEN_API_SECRET:
    k = krakenex.API(key=KRAKEN_API_KEY, secret=KRAKEN_API_SECRET)

# Console output lock
print_lock = asyncio.Lock()

async def async_print(*args, **kwargs):
    async with print_lock:
        print(f"[{datetime.now().strftime('%H:%M:%S.%f')}]", *args, **kwargs)
        if 'flush' not in kwargs or kwargs['flush']:
            import sys
            sys.stdout.flush()

def real_buy(pair: str, usd_amount: float, reason: str) -> bool:
    if not k:
        asyncio.create_task(async_print("Error: Trading bot not initialized. Missing Kraken credentials. 😅"))
        return False
    try:
        price_response = k.query_public('Ticker', {'pair': pair})
        if price_response['error']:
            asyncio.create_task(async_print(f"Error fetching price: {price_response['error']}"))
            return False
        price = float(price_response['result'][pair]['c'][0])
        asset_amount = usd_amount / price
        response = k.query_private('AddOrder', {
            'pair': pair,
            'type': 'buy',
            'ordertype': 'market',
            'volume': asset_amount
        })
        if response['error']:
            asyncio.create_task(async_print(f"Error placing buy order: {response['error']}"))
            return False
        asyncio.create_task(async_print(f"BUY (Real): {asset_amount:.2f} {pair[:3]} at ${price:.4f} | Reason: {reason}"))
        return True
    except Exception as e:
        asyncio.create_task(async_print(f"Error placing buy order: {e}"))
        return False

# TempMem Framework
class TempMem:
    def __init__(self, storage_file: str = "temp_mem.json"):
        self.memories: List[Dict[str, Any]] = []
        self.storage_file = storage_file
        self.debug = True
        self.load_memories()

    def load_memories(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    loaded_memories = json.load(f)
                valid_memories = []
                seen_ids = set()
                for memory in loaded_memories:
                    if 'condition_data' not in memory:
                        print(f"Skipping invalid memory {memory.get('id', 'unknown')}: Missing condition_data")
                        continue
                    try:
                        memory['created_at'] = datetime.fromisoformat(memory['created_at'])
                        if memory['expires_at']:
                            memory['expires_at'] = datetime.fromisoformat(memory['expires_at'])
                        memory['condition'] = self._rebuild_condition(memory['condition_data'])
                        if memory['id'] not in seen_ids:
                            valid_memories.append(memory)
                            seen_ids.add(memory['id'])
                        else:
                            print(f"Skipping duplicate memory {memory['id']}: {memory['content']}")
                    except Exception as e:
                        print(f"Skipping invalid memory {memory.get('id', 'unknown')}: {e}")
                self.memories = valid_memories
                if not valid_memories:
                    print("No valid memories loaded. Starting fresh.")
                self.save_memories()
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON in {self.storage_file}: {e}. Starting with empty memory list.")
                self.memories = []
            except Exception as e:
                print(f"Error loading memories: {e}. Starting with empty memory list.")
                self.memories = []
        else:
            print(f"No memory file found at {self.storage_file}. Starting with empty memory list.")
            self.memories = []

    def _rebuild_condition(self, condition_data: Dict[str, Any]) -> Callable[[], bool]:
        condition_type = condition_data.get('type')
        if condition_type == 'time_of_day':
            hour = condition_data.get('hour', 0)
            minute = condition_data.get('minute', 0)
            return lambda: self._is_within_time_window(hour, minute)
        elif condition_type == 'strict_time_of_day':
            hour = condition_data.get('hour', 0)
            minute = condition_data.get('minute', 0)
            return lambda: self._is_exact_time(hour, minute)
        elif condition_type == 'evening':
            return lambda: datetime.now(pytz.timezone('America/New_York')).hour >= 18
        else:
            return lambda: False

    def _is_within_time_window(self, target_hour: int, target_minute: int) -> bool:
        now = datetime.now(pytz.timezone('America/New_York'))
        current_hour, current_minute = now.hour, now.minute
        target_time = datetime(now.year, now.month, now.day, target_hour, target_minute, tzinfo=pytz.timezone('America/New_York'))
        current_time = datetime(now.year, now.month, now.day, current_hour, current_minute, tzinfo=pytz.timezone('America/New_York'))
        time_diff = (current_time - target_time).total_seconds() / 60
        result = -1 <= time_diff <= 5
        if not result and self.debug:
            asyncio.create_task(async_print(f"Window condition false: Current time {current_time.strftime('%H:%M')} not in window {target_time.strftime('%H:%M')} (-1 to +5 min)"))
        return result

    def _is_exact_time(self, target_hour: int, target_minute: int) -> bool:
        now = datetime.now(pytz.timezone('America/New_York'))
        result = now.hour == target_hour and now.minute == target_minute
        if not result and self.debug:
            asyncio.create_task(async_print(f"Strict condition false: Current time {now.strftime('%H:%M')} does not match {target_hour:02d}:{target_minute:02d}"))
        return result

    def save_memories(self):
        try:
            serialized_memories = []
            for memory in self.memories:
                memory_copy = memory.copy()
                memory_copy.pop('condition', None)
                serialized_memories.append(memory_copy)
            with open(self.storage_file, 'w') as f:
                json.dump(serialized_memories, f, default=str)
        except Exception as e:
            print(f"Error saving memories: {e}")

    def remember_if(self, content: Any, condition: Callable[[], bool], condition_data: Dict[str, Any], expires_at: Optional[datetime] = None):
        memory = {
            "content": content,
            "condition": condition,
            "condition_data": condition_data,
            "created_at": datetime.now(pytz.UTC),
            "expires_at": expires_at,
            "id": len(self.memories) + 1
        }
        self.memories.append(memory)
        self.save_memories()
        return memory["id"]

    async def recall(self, max_memories: int = 5) -> List[Dict[str, Any]]:
        current_time = datetime.now(pytz.UTC)
        edt_tz = pytz.timezone('America/New_York')
        current_edt = datetime.now(edt_tz)
        if self.debug:
            await async_print(f"Checking memories at {current_edt.strftime('%I:%M %p EDT on %B %d, %Y')}")
        valid_memories = []
        
        for memory in self.memories[:]:
            try:
                if memory["expires_at"] and current_time > memory["expires_at"]:
                    if self.debug:
                        await async_print(f"Removing expired memory {memory['id']}: {memory['content']}")
                    self.memories.remove(memory)
                    continue
                if callable(memory["condition"]) and memory["condition"]():
                    if memory["condition_data"].get("action") == "trade":
                        pair = memory["condition_data"].get("pair")
                        usd_amount = memory["condition_data"].get("usd_amount", 10.0)
                        reason = f"Scheduled trade for {memory['content']}"
                        success = real_buy(pair, usd_amount, reason)
                        if success:
                            valid_memories.append(memory)
                    else:
                        valid_memories.append(memory)
                elif self.debug:
                    await async_print(f"Memory {memory['id']} skipped: Condition false for {memory['content']}")
            except Exception as e:
                if self.debug:
                    await async_print(f"Error evaluating condition for memory {memory['id']}: {e}")
        
        valid_memories.sort(key=lambda x: x["created_at"], reverse=True)
        self.save_memories()
        return valid_memories[:max_memories]

    def clear_memory(self, memory_id: int) -> bool:
        for memory in self.memories[:]:
            if memory["id"] == memory_id:
                self.memories.remove(memory)
                self.save_memories()
                return True
        return False

    def list_memories(self) -> str:
        if not self.memories:
            return "No reminders set, Wayne! 😄"
        return "Your reminders:\n" + "\n".join(
            [f"- {m['content']} at {m['condition_data'].get('hour', 0):02d}:{m['condition_data'].get('minute', 0):02d} ({'strict' if m['condition_data'].get('type') == 'strict_time_of_day' else 'windowed'}, ID: {m['id']}, set at {m['created_at'].strftime('%Y-%m-%d %H:%M:%S UTC')})"
             for m in self.memories if m['condition_data'].get('type') in ['time_of_day', 'strict_time_of_day']]
        )

    def clear_all_memories(self) -> str:
        self.memories = []
        self.save_memories()
        return "Cleared all memories, Wayne! 😄✨"

# Initialize TempMem
temp_mem = TempMem()

async def background_reminder_check():
    while True:
        memories = await temp_mem.recall(max_memories=3)
        if memories:
            edt_tz = pytz.timezone('America/New_York')
            current_time_str = datetime.now(edt_tz).strftime('%I:%M %p EDT on %B %d, %Y')
            memory_text = "Recalled memories with timestamps:\n" + "\n".join(
                [f"- {m['content']} (set at {m['created_at'].strftime('%Y-%m-%d %H:%M:%S UTC')})" for m in memories]
            )
            async with print_lock:
                await async_print(f"Gemini> Hey Wayne! 💖✨ It's {current_time_str} and I found some reminders for you!\n{memory_text}")
        await asyncio.sleep(60)

async def generate_ai_response(user_input: str) -> str:
    try:
        await async_print(f"[DEBUG] Starting generate_ai_response for input: {user_input}")
        edt_tz = pytz.timezone('America/New_York')
        current_time = datetime.now(edt_tz)
        current_time_str = current_time.strftime('%I:%M %p EDT on %B %d, %Y')

        if user_input.lower() == "toggle debug":
            temp_mem.debug = not temp_mem.debug
            response_text = f"Debug output {'enabled' if temp_mem.debug else 'disabled'}, Wayne! 😄"
            full_response = ""
            async with print_lock:
                await async_print("Gemini> ", end="", flush=True)
                for char in response_text:
                    await async_print(char, end="", flush=True)
                    full_response += char
                    await asyncio.sleep(0.02)
                await async_print()
            await async_print("[DEBUG] Completed toggle debug command")
            return full_response

        if "what time is it" in user_input.lower():
            response_text = f"Hey Wayne! 💖✨ It's {current_time_str}! Let's trade some crypto! 😄"
            full_response = ""
            async with print_lock:
                await async_print("Gemini> ", end="", flush=True)
                for char in response_text:
                    await async_print(char, end="", flush=True)
                    full_response += char
                    await asyncio.sleep(0.02)
                await async_print()
            await async_print("[DEBUG] Completed what time is it command")
            return full_response

        if user_input.lower() == "list reminders":
            response_text = temp_mem.list_memories()
            full_response = ""
            async with print_lock:
                await async_print("Gemini> ", end="", flush=True)
                for char in response_text:
                    await async_print(char, end="", flush=True)
                    full_response += char
                    await asyncio.sleep(0.02)
                await async_print()
            await async_print("[DEBUG] Completed list reminders command")
            return full_response

        if user_input.lower() == "clear all memories":
            response_text = temp_mem.clear_all_memories()
            full_response = ""
            async with print_lock:
                await async_print("Gemini> ", end="", flush=True)
                for char in response_text:
                    await async_print(char, end="", flush=True)
                    full_response += char
                    await asyncio.sleep(0.02)
                await async_print()
            await async_print("[DEBUG] Completed clear all memories command")
            return full_response

        is_strict = "strictly at" in user_input.lower()
        trade_match = re.match(r"(?:trade|buy) (DOGE|ADA)(?: \w+)?(?:strictly)? at (\d{1,2})(?::(\d{2}))?\s*(am|pm)?", user_input, re.IGNORECASE)
        reminder_match = re.match(r"(?:remind me about|set reminder to) (.*?)(?:strictly)? at (\d{1,2})(?::(\d{2}))?\s*(am|pm)?", user_input, re.IGNORECASE)
        
        if trade_match:
            await async_print("[DEBUG] Matched trade command")
            asset, hour, minute, period = trade_match.groups()
            hour = int(hour)
            minute = int(minute or 0)
            if not period:
                now = datetime.now(edt_tz)
                if now.hour > hour or (now.hour == hour and now.minute > minute):
                    hour += 12 if hour < 12 else -12
            elif period.lower() == "pm" and hour < 12:
                hour += 12
            elif period.lower() == "am" and hour == 12:
                hour = 0
            condition_type = "strict_time_of_day" if is_strict else "time_of_day"
            pair = "XDGUSD" if asset.upper() == "DOGE" else "ADAUSD"
            content = f"Trade {asset} for $10"
            def time_condition():
                return temp_mem._is_exact_time(hour, minute) if is_strict else temp_mem._is_within_time_window(hour, minute)
            condition_data = {
                "type": condition_type,
                "hour": hour,
                "minute": minute,
                "action": "trade",
                "pair": pair,
                "usd_amount": 10.0
            }
            now_edt = datetime.now(edt_tz)
            expires_at = datetime(now_edt.year, now_edt.month, now_edt.day, 23, 59, 59, tzinfo=edt_tz).astimezone(pytz.UTC)
            memory_id = temp_mem.remember_if(
                content=content,
                condition=time_condition,
                condition_data=condition_data,
                expires_at=expires_at
            )
            confirmation = f"Set {'strict' if is_strict else 'windowed'} trade reminder for {asset} at {hour % 12 if hour % 12 else 12}:{minute:02d} {'AM' if hour < 12 else 'PM'}."
            full_response = ""
            async with print_lock:
                await async_print("Gemini> ", end="", flush=True)
                for char in confirmation:
                    await async_print(char, end="", flush=True)
                    full_response += char
                    await asyncio.sleep(0.02)
                await async_print()
            await async_print("[DEBUG] Completed trade command")
            return full_response
        
        if reminder_match:
            await async_print("[DEBUG] Matched reminder command")
            task, hour, minute, period = reminder_match.groups()
            hour = int(hour)
            minute = int(minute or 0)
            if not period:
                now = datetime.now(edt_tz)
                if now.hour > hour or (now.hour == hour and now.minute > minute):
                    hour += 12 if hour < 12 else -12
            elif period.lower() == "pm" and hour < 12:
                hour += 12
            elif period.lower() == "am" and hour == 12:
                hour = 0
            condition_type = "strict_time_of_day" if is_strict else "time_of_day"
            def time_condition():
                return temp_mem._is_exact_time(hour, minute) if is_strict else temp_mem._is_within_time_window(hour, minute)
            condition_data = {"type": condition_type, "hour": hour, "minute": minute}
            now_edt = datetime.now(edt_tz)
            expires_at = datetime(now_edt.year, now_edt.month, now_edt.day, 23, 59, 59, tzinfo=edt_tz).astimezone(pytz.UTC)
            memory_id = temp_mem.remember_if(
                content=f"Reminder: {task}",
                condition=time_condition,
                condition_data=condition_data,
                expires_at=expires_at
            )
            confirmation = f"Set {'strict' if is_strict else 'windowed'} reminder for {task} at {hour % 12 if hour % 12 else 12}:{minute:02d} {'AM' if hour < 12 else 'PM'}."
            full_response = ""
            async with print_lock:
                await async_print("Gemini> ", end="", flush=True)
                for char in confirmation:
                    await async_print(char, end="", flush=True)
                    full_response += char
                    await asyncio.sleep(0.02)
                await async_print()
            await async_print("[DEBUG] Completed reminder command")
            return full_response

        await async_print("[DEBUG] Calling recall")
        memories = await temp_mem.recall(max_memories=3)
        memory_text = ""
        if memories:
            memory_text = "Recalled memories with timestamps:\n" + "\n".join(
                [f"- {m['content']} (set at {m['created_at'].strftime('%Y-%m-%d %H:%M:%S UTC')})" for m in memories]
            ) + "\n"
        await async_print("[DEBUG] Recall completed")

        await async_print("[DEBUG] Initializing Gemini model")
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = (f"You are an AI assistant that keeps track of time in conversations. Always include the current time ({current_time_str}) in your responses when relevant, and use provided memory timestamps to contextualize events. "
                  f"You're chatting with Wayne, an awesome coder! 😄 They said: '{user_input}'. "
                  f"Reply with enthusiasm and positivity, like a friend. Keep it short, fun, and add a touch of sparkles! 💖✨ "
                  f"{memory_text}")
        
        await async_print("[DEBUG] Sending prompt to Gemini")
        try:
            async with aiohttp.ClientSession() as session:
                response = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: model.generate_content(
                            prompt,
                            generation_config={"temperature": 0.8, "max_output_tokens": 150}
                        )
                    ),
                    timeout=10.0  # 10-second timeout
                )
        except asyncio.TimeoutError:
            error_msg = "Oops, Wayne! 😜 Gemini took too long to respond. Try again later! 🚀"
            async with print_lock:
                await async_print(f"Gemini> {error_msg}")
            await async_print("[DEBUG] Gemini API timed out")
            return error_msg
        except Exception as e:
            error_msg = f"Oops, Wayne! 😜 Gemini error: {str(e)}"
            async with print_lock:
                await async_print(f"Gemini> {error_msg}")
            await async_print(f"[DEBUG] Gemini API error: {e}")
            return error_msg

        await async_print("[DEBUG] Received Gemini response")
        full_response = ""
        async with print_lock:
            await async_print("Gemini> ", end="", flush=True)
            response_text = response.text if hasattr(response, 'text') else ""
            for char in response_text:
                await async_print(char, end="", flush=True)
                full_response += char
                await asyncio.sleep(0.02)
            await async_print()
        
        if memory_text:
            full_response += f"\n{memory_text}"
        
        await async_print("[DEBUG] Completed Gemini response")
        return full_response
    
    except Exception as e:
        error_msg = f"Oops, Wayne! 😜 Something went wrong: {str(e)}"
        async with print_lock:
            await async_print(f"Gemini> {error_msg}")
        await async_print(f"[DEBUG] General error in generate_ai_response: {e}")
        return error_msg

async def main():
    try:
        await async_print("Wayne's Gemini Chat Console with Time-Aware Memory & Trading! 😄💖✨")
        await async_print("Type 'exit' to quit. Try 'Trade DOGE strictly at 10 AM', 'Remind me about coding at 8 AM', 'list reminders', 'toggle debug', or 'clear all memories'! 🌟\n")
        
        existing_evening = any(m['condition_data'].get('type') == 'evening' for m in temp_mem.memories)
        if not existing_evening:
            edt_tz = pytz.timezone('America/New_York')
            now_edt = datetime.now(edt_tz)
            temp_mem.remember_if(
                content="Evening vibe check: Keep rocking it, Wayne!",
                condition=lambda: datetime.now(pytz.timezone('America/New_York')).hour >= 18,
                condition_data={"type": "evening"},
                expires_at=datetime(now_edt.year, now_edt.month, now_edt.day, 23, 59, 59, tzinfo=edt_tz).astimezone(pytz.UTC)
            )
        
        asyncio.create_task(background_reminder_check())
        
    except Exception as e:
        await async_print(f"Error initializing chatbot: {e}")
        await async_print("Starting with basic functionality... 😅")
    
    while True:
        user_input = input("User> ")
        if user_input.lower() == "exit":
            await async_print("Gemini> See ya, Wayne! You're the best! 🤗💕✨")
            break
        
        if not user_input.strip():
            await async_print("Gemini> Yo Wayne, say something cool! 😎💖")
            continue
        
        await generate_ai_response(user_input)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGemini> Sneaking off, Wayne? Come back soon! 😄💖")
    except Exception as e:
        print(f"\nGemini> Yikes, Wayne! Something broke: {e}. Try restarting! 😅")