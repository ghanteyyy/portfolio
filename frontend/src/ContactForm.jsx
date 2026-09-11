import { request } from './request';
import React, { useRef, useState } from 'react';

function validateField(name, rawValue) {
	const value = rawValue.trim();
	if (name === 'name') {
		if (!value) return ['Please enter your name.'];
		if (value.length > 120) return ['Please keep your name under 121 characters.'];
	}
	if (name === 'email') {
		if (!value) return ['Please enter your email address.'];
		if (value.length > 254 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value))
			return ['Enter a valid email address, such as you@example.com.'];
	}
	if (name === 'message') {
		if (!value) return ['Please write a message before sending.'];
		if (value.length > 5000) return ['Please keep your message within 5,000 characters.'];
	}
	return null;
}

export default function ContactForm() {
	const [status, setStatus] = useState('idle');
	const [notice, setNotice] = useState('');
	const [errors, setErrors] = useState({});
	const submitting = useRef(false);

	function updateError(event) {
		const { name, value } = event.target;
		if (!errors[name]) return;
		const error = validateField(name, value);
		setErrors((previous) => {
			const next = { ...previous };
			if (error) next[name] = error;
			else delete next[name];
			return next;
		});
		setNotice('');
	}

	async function submit(event) {
		event.preventDefault();
		if (submitting.current) return;
		const form = event.currentTarget;
		const payload = Object.fromEntries(new FormData(form));
		const fieldErrors = {};
		for (const name of ['name', 'email', 'message']) {
			payload[name] = payload[name].trim();
			const error = validateField(name, payload[name]);
			if (error) fieldErrors[name] = error;
		}
		if (Object.keys(fieldErrors).length) {
			setErrors(fieldErrors);
			setStatus('error');
			setNotice('Please correct the highlighted fields and try again.');
			form.elements.namedItem(Object.keys(fieldErrors)[0])?.focus();
			return;
		}
		submitting.current = true;
		setStatus('sending');
		setNotice('');
		setErrors({});
		try {
			const tokenResponse = await request('/api/contact/token/', { credentials: 'same-origin' });
			if (!tokenResponse.ok) throw new Error('Unable to connect. Please try again.');
			const { csrfToken } = await tokenResponse.json();
			const response = await request('/api/contact/', {
				method: 'POST',
				credentials: 'same-origin',
				headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
				body: JSON.stringify(payload),
			});
			const result = await response.json().catch(() => ({}));
			if (!response.ok) {
				setErrors(result.errors || {});
				const firstField = Object.keys(result.errors || {})[0];
				if (firstField) form.elements.namedItem(firstField)?.focus();
				throw new Error(result.error || 'Your message could not be sent. Please try again.');
			}
			form.reset();
			setStatus('success');
			setNotice(result.message);
		} catch (error) {
			setStatus('error');
			setNotice(
				error instanceof TypeError
					? 'Connection interrupted. Your message is still here; please try again.'
					: error.message,
			);
		} finally {
			submitting.current = false;
		}
	}

	return (
		<form
			className="message-form"
			noValidate
			onSubmit={submit}
			onChange={updateError}
			aria-labelledby="message-heading"
			aria-busy={status === 'sending'}
		>
			<h3 id="message-heading">Send a message</h3>
			<div className="message-fields">
				<div className="message-field">
					<label htmlFor="contact-name">Your name</label>
					<input
						id="contact-name"
						name="name"
						autoComplete="name"
						placeholder="Your name"
						required
						maxLength={120}
						aria-invalid={Boolean(errors.name)}
						aria-describedby={errors.name ? 'name-error' : undefined}
					/>
					{errors.name && (
						<span className="field-error" id="name-error">
							{errors.name.join(' ')}
						</span>
					)}
				</div>
				<div className="message-field">
					<label htmlFor="contact-email">Email address</label>
					<input
						id="contact-email"
						name="email"
						type="email"
						autoComplete="email"
						placeholder="you@example.com"
						required
						maxLength={254}
						aria-invalid={Boolean(errors.email)}
						aria-describedby={errors.email ? 'email-error' : undefined}
					/>
					{errors.email && (
						<span className="field-error" id="email-error">
							{errors.email.join(' ')}
						</span>
					)}
				</div>
			</div>
			<div className="message-field">
				<label htmlFor="contact-message">Your message</label>
				<textarea
					id="contact-message"
					name="message"
					rows={4}
					placeholder="Tell me a little about what you have in mind…"
					required
					maxLength={5000}
					aria-invalid={Boolean(errors.message)}
					aria-describedby={errors.message ? 'message-error' : undefined}
				/>
				{errors.message && (
					<span className="field-error" id="message-error">
						{errors.message.join(' ')}
					</span>
				)}
			</div>
			<div className="form-trap" aria-hidden="true">
				<label htmlFor="contact-website">Leave this empty</label>
				<input id="contact-website" name="website" tabIndex={-1} autoComplete="off" />
			</div>
			<div className="message-actions">
				<button className="button dark" type="submit" disabled={status === 'sending'}>
					{status === 'sending' ? 'Sending…' : 'Send message'}{' '}
					<i className="fa-solid fa-paper-plane" aria-hidden="true" />
				</button>
			</div>
			<p className={`message-notice ${status}`} role="status" aria-live="polite">
				{notice}
			</p>
		</form>
	);
}
