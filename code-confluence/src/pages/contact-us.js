import React, { useState } from 'react';
import Layout from '@theme/Layout';

export default function Contact() {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    message: '',
  });

  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const validateForm = () => {
    let newErrors = {};

    // Name validation (no numbers allowed)
    if (!/^[a-zA-Z\s]*$/.test(formData.firstName)) {
      newErrors.firstName = 'First name should not contain numbers';
    }
    if (!/^[a-zA-Z\s]*$/.test(formData.lastName)) {
      newErrors.lastName = 'Last name should not contain numbers';
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    // Message validation (not empty)
    if (formData.message.trim() === '') {
      newErrors.message = 'Message cannot be empty';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      console.log('Form submitted:', formData);
      // Here you would typically send the form data to a server
      setFormData({ firstName: '', lastName: '', email: '', message: '' });
      setErrors({});
    } else {
      console.log('Form has errors');
    }
  };

  return (
    <Layout title="Contact Us">
      <div style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto', display: 'flex', gap: '2rem' }}>
        <div style={{ flex: 1 }}>
          <h1 style={{ marginBottom: '1rem' }}>Contact Us</h1>
          <p style={{ marginBottom: '2rem' }}>Please fill this form in a decent manner</p>
          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '1.5rem' }}>
              <label htmlFor="fullName" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>Full Name *</label>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <div style={{ flex: 1 }}>
                  <input
                    type="text"
                    id="firstName"
                    name="firstName"
                    value={formData.firstName}
                    onChange={handleChange}
                    required
                    placeholder="First Name"
                    style={{ width: '100%', padding: '0.5rem', border: '1px solid #ccc', borderRadius: '4px' }}
                  />
                  {errors.firstName && <div style={{ color: 'red', fontSize: '0.8rem' }}>{errors.firstName}</div>}
                </div>
                <div style={{ flex: 1 }}>
                  <input
                    type="text"
                    id="lastName"
                    name="lastName"
                    value={formData.lastName}
                    onChange={handleChange}
                    required
                    placeholder="Last Name"
                    style={{ width: '100%', padding: '0.5rem', border: '1px solid #ccc', borderRadius: '4px' }}
                  />
                  {errors.lastName && <div style={{ color: 'red', fontSize: '0.8rem' }}>{errors.lastName}</div>}
                </div>
              </div>
            </div>
            <div style={{ marginBottom: '1.5rem' }}>
              <label htmlFor="email" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>E-mail *</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                placeholder="example@example.com"
                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ccc', borderRadius: '4px' }}
              />
              {errors.email && <div style={{ color: 'red', fontSize: '0.8rem' }}>{errors.email}</div>}
            </div>
            <div style={{ marginBottom: '1.5rem' }}>
              <label htmlFor="message" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>Message *</label>
              <textarea
                id="message"
                name="message"
                value={formData.message}
                onChange={handleChange}
                required
                style={{ width: '100%', padding: '0.5rem', border: '1px solid #ccc', borderRadius: '4px', minHeight: '150px' }}
              />
              {errors.message && <div style={{ color: 'red', fontSize: '0.8rem' }}>{errors.message}</div>}
            </div>
            <button type="submit" style={{
              padding: '0.75rem 2rem',
              backgroundColor: '#000',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '1rem',
              fontWeight: 'bold'
            }}>
              SUBMIT
            </button>

          </form>
        </div>
        <div style={{ flex: 1 }}>
          <h2 style={{ marginBottom: '1rem' }}>Contacts</h2>
          <div style={{ marginBottom: '1.5rem' }}>
            <h3>Jay Ghiya</h3>
            <p>Contact: <a href="mailto:jayghiya@unoplat.co.in">jayghiya@unoplat.co.in</a></p>
          </div>
          <div style={{ marginBottom: '1.5rem' }}>
            <h3>Vipin Shreyas Kumar</h3>
            <p>Contact: <a href="mailto:vipinshreyaskumar@unoplat.co.in">vipinshreyaskumar@unoplat.co.in</a></p>
          </div>
          <div style={{ marginBottom: '1.5rem' }}>
            <h3>Book a call with us</h3>
            <p><a href="https://cal.com/your-cal-link" target="_blank" rel="noopener noreferrer">Cal Link</a></p>
          </div>
          <div style={{ marginBottom: '1.5rem' }}>
            <h3>Discord Community Channel</h3>
            <p><a href="https://discord.gg/your-discord-invite" target="_blank" rel="noopener noreferrer">unoplat's server code-confluence</a></p>
          </div>
          <div>
            <h3>Twitter</h3>
            <p><a href="https://x.com/unoplatio" target="_blank" rel="noopener noreferrer">Reach out to us on Twitter</a></p>
          </div>
        </div>
      </div>
    </Layout>
  );
}