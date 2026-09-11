import { request } from './request';
import React, { useEffect, useRef, useState } from 'react';

export default function ProfilePhoto({ profile, onUploaded }) {
	const [file, setFile] = useState(null),
		[preview, setPreview] = useState(''),
		[error, setError] = useState(''),
		[busy, setBusy] = useState(false),
		[notice, setNotice] = useState('');
	const input = useRef(null);
	useEffect(() => {
		if (!file) {
			setPreview('');
			return;
		}
		const url = URL.createObjectURL(file);
		setPreview(url);
		return () => URL.revokeObjectURL(url);
	}, [file]);
	function select(event) {
		setNotice('');
		setError('');
		const next = event.target.files?.[0];
		setFile(null);
		if (!next) return;
		if (!['image/jpeg', 'image/png', 'image/webp'].includes(next.type)) {
			setError('Choose a JPEG, PNG, or WebP image.');
			event.target.value = '';
			return;
		}
		if (next.size > 5 * 1024 * 1024) {
			setError('Choose an image smaller than 5 MB.');
			event.target.value = '';
			return;
		}
		setFile(next);
	}
	async function upload() {
		if (!file || busy) return;
		setBusy(true);
		setError('');
		setNotice('');
		try {
			const tokenResponse = await request('/api/contact/token/');
			if (!tokenResponse.ok) throw new Error('Unable to connect. Please try again.');
			const { csrfToken } = await tokenResponse.json();
			const data = new FormData();
			data.append('photo', file);
			const response = await request(`/api/studio/profile/${profile.id}/photo/`, {
				method: 'POST',
				credentials: 'same-origin',
				headers: { 'X-CSRFToken': csrfToken },
				body: data,
			});
			const result = await response.json().catch(() => ({}));
			if (!response.ok) throw new Error(result.error || 'Upload failed. Please try again.');
			onUploaded(result);
			setFile(null);
			if (input.current) input.current.value = '';
			setNotice('Photo updated on your portfolio.');
		} catch (e) {
			setError(e.message);
		} finally {
			setBusy(false);
		}
	}
	const saved = profile.photo ? `/media/${profile.photo}` : '/santosh-karki.jpg';
	return (
		<section className="rs-photo-editor" aria-labelledby="photo-heading">
			<img
				src={preview || saved}
				alt={file ? 'Preview of selected portrait' : 'Current portfolio portrait'}
				width="120"
				height="120"
			/>
			<div>
				<h3 id="photo-heading">Portfolio photo</h3>
				<p>JPEG, PNG, or WebP · Up to 5 MB. Your portrait is displayed in a circle.</p>
				{profile.id ? (
					<>
						<label htmlFor="profile-photo">Choose a new photo</label>
						<input
							ref={input}
							id="profile-photo"
							type="file"
							accept="image/jpeg,image/png,image/webp"
							onChange={select}
							disabled={busy}
							aria-describedby="photo-feedback"
						/>
						<div className="rs-photo-actions">
							<button
								type="button"
								className="rs-primary"
								disabled={!file || busy}
								onClick={upload}
							>
								{busy ? 'Uploading…' : 'Upload photo'}
							</button>
							{file && (
								<button
									type="button"
									className="rs-secondary"
									disabled={busy}
									onClick={() => {
										setFile(null);
										input.current.value = '';
									}}
								>
									Cancel selection
								</button>
							)}
						</div>
					</>
				) : (
					<p>Save your profile first, then upload a photo.</p>
				)}
				<div id="photo-feedback" aria-live="polite">
					{error && (
						<p className="rs-field-error" role="alert">
							{error}
						</p>
					)}
					{notice && (
						<p className="rs-photo-success" role="status">
							{notice}
						</p>
					)}
				</div>
			</div>
		</section>
	);
}
