import React, { useState } from 'react';
import Layout from '@theme/Layout';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faDiscord, faTwitter } from '@fortawesome/free-brands-svg-icons'
import styles from '../css/contact-us.module.css';
import { faPhone, faMapMarkerAlt } from '@fortawesome/free-solid-svg-icons';
import emailjs from 'emailjs-com';

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

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (validateForm()) {
      emailjs.send('service_gp4ccmu', 'template_3m1nbg5', formData, 'pevo5K5mvmR54CoKy')
        .then((result) => {
          console.log(result.text);
          alert('Message sent successfully!');
          setFormData({ firstName: '', lastName: '', email: '', message: '' }); // Clear form
        }, (error) => {
          console.log(error.text);
          alert('Failed to send message. Please try again.');
        });
    } else {
      console.log('Form has errors');
    }
  };

  return (
    <Layout title="Contact Us">
      <div style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto', display: 'flex', gap: '6rem' }}>
        <div style={{ backgroundColor: '#ffffff', padding: '4rem', boxShadow: '0 4px 8px 0 rgba(0,0,0,0.2), 0 6px 20px 0 rgba(0,0,0,0.19)' }}>
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
        </div>
        <div style={{ flex: 1 }}>

          {/* <div className={styles.locationContainer}>
            <FontAwesomeIcon icon={faMapMarkerAlt} className={styles.locationIcon} />
            <div className={styles.locationInfo}>
              <h3 className={styles.locationTitle}>Location</h3>
              <a
                href="https://www.google.com/maps/search/?api=1&query=Gf-10+Allen+Complex,+Nizampura+Rd,+Nizampura+Char+Rasta,+LG+Nagar-390002,+Vadodara,+Gujarat"
                target="_blank"
                rel="noopener noreferrer"
                className={styles.mapLink}
              >
                <p className={styles.locationAddress}>
                  Gf-10 Allen Complex,<br />
                  Nizampura Rd, Nizampura Char Rasta,<br />
                  LG Nagar-390002, Vadodara, Gujarat
                </p>
              </a>
            </div>

          </div> */}
          {/* <div style={{ width:'fit-content',height:'fit-content',padding:'1rem',border:'1px solid #e0e0e0',boxSizing:'border-box',borderRadius:'12px',backgroundColor:'#f8f8f8',boxShadow:'0 2px 4px rgba(0, 0, 0, 0.05);',display:'flex',flexDirection:'column',gap:'1rem' }}> */}
          <h2 style={{marginTop:'1rem'}}>Contact Details</h2>
            <div>
              <a href="https://cal.com/jay-ghiya/15min" className={styles.bookCallLink}>
                <FontAwesomeIcon icon={faPhone} className={styles.callIcon} />
              <span>Book a Call</span>
              </a>
            </div>

            <div className={styles.socialLinksContainer}>
              <a href="https://discord.com/channels/1131597983058755675/1169968780953260106" className={`${styles.socialLink} ${styles.discordLink}`}>
                <FontAwesomeIcon icon={faDiscord} className={styles.icon} />
              </a>
              <a href="https://x.com/unoplatio" className={`${styles.socialLink} ${styles.twitterLink}`}>
                <FontAwesomeIcon icon={faTwitter} className={styles.icon} />
              </a>
            </div>
          {/* </div> */}
        </div>
      </div>
    </Layout>
  );
}