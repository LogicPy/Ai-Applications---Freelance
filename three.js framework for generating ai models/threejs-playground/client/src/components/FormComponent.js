import React from 'react';
import './FormComponent.css'; // Optional: For additional styling

function FormComponent() {
  return (
    <div className="form-component">
      <h2>Contact Us</h2>
      <form>
        <label htmlFor="name">Name:</label>
        <input type="text" id="name" name="name" placeholder="Your name.." />

        <label htmlFor="email">Email:</label>
        <input type="email" id="email" name="email" placeholder="Your email.." />

        <label htmlFor="message">Message:</label>
        <textarea id="message" name="message" placeholder="Write something.." rows="5"></textarea>

        <input type="submit" value="Submit" />
      </form>
    </div>
  );
}

export default FormComponent;
