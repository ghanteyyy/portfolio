import { request } from './request';
import React, { useEffect, useState } from 'react';
import './studio.css';
import ProfilePhoto from './ProfilePhoto';

const sections = {
	overview: ['Overview', 'chart-simple'],
	projects: ['Projects', 'layer-group'],
	experience: ['Experience', 'briefcase'],
	profile: ['Profile', 'user'],
	messages: ['Messages', 'envelope'],
};
const fields = {
	projects: {
		title: 'Title',
		category: 'Category',
		description: 'Description',
		tags: 'Tags (JSON list)',
		url: 'Repository URL',
		order: 'Display order',
	},
	experience: {
		role: 'Role',
		organization: 'Organization',
		location: 'Location',
		period: 'Period',
		description: 'Responsibilities (one point per line)',
		order: 'Display order',
	},
	profile: {
		name: 'Name',
		role: 'Role',
		summary: 'Summary',
		email: 'Email',
		phone: 'Phone',
		location: 'Location',
		github: 'GitHub URL',
		linkedin: 'LinkedIn URL',
		skills: 'Skills (JSON)',
		education: 'Education (JSON)',
	},
};
const jsonFields = ['tags', 'skills', 'education'];
const longFields = ['description', 'summary', ...jsonFields];
const icon = (name) => <i className={`fa-solid fa-${name}`} aria-hidden="true" />;

async function api(path, method = 'GET', data) {
	const headers = {};
	if (method !== 'GET') {
		const tokenResponse = await request('/api/contact/token/', { credentials: 'same-origin' });
		if (!tokenResponse.ok) throw new Error('Unable to connect. Please try again.');
		headers['X-CSRFToken'] = (await tokenResponse.json()).csrfToken;
		headers['Content-Type'] = 'application/json';
	}
	const response = await request(`/api/studio/${path}`, {
		method,
		credentials: 'same-origin',
		headers,
		body: data === undefined ? undefined : JSON.stringify(data),
	});
	const result = await response.json().catch(() => ({}));
	if (!response.ok) {
		const error = new Error(result.error || 'Something went wrong. Please try again.');
		error.status = response.status;
		error.fields = result.errors || {};
		throw error;
	}
	return result;
}

function Login({ onLogin }) {
	const [error, setError] = useState(''),
		[busy, setBusy] = useState(false);
	async function submit(event) {
		event.preventDefault();
		if (busy) return;
		const data = Object.fromEntries(new FormData(event.currentTarget));
		if (!data.email.trim() || !data.password) {
			setError('Enter your email and password.');
			return;
		}
		setBusy(true);
		setError('');
		try {
			onLogin(await api('session/', 'POST', data));
		} catch (e) {
			setError(e.message);
		} finally {
			setBusy(false);
		}
	}
	return (
		<div className="rs-login">
			<div className="rs-login-card">
				<section className="rs-login-story">
					<a href="/" className="rs-logo">
						sk<span>.</span>
						<small>PORTFOLIO STUDIO</small>
					</a>
					<div>
						<span className="rs-eyebrow">A SPACE FOR WHAT YOU BUILD</span>
						<h1>
							Your work.
							<br />
							Your story.
							<br />
							<em>Your studio.</em>
						</h1>
						<p>
							Great work deserves a place to grow.
							<br />
							Keep yours moving forward.
						</p>
					</div>
					<span className="rs-eyebrow">BUILT WITH PURPOSE.</span>
				</section>
				<section className="rs-login-form">
					<a href="/" className="rs-back">
						← Back to portfolio
					</a>
					<div>
						<span className="rs-eyebrow">WELCOME BACK</span>
						<h2>
							Make yourself
							<br />
							<em>at home.</em>
						</h2>
						<p>Sign in to manage your portfolio and messages.</p>
						<form onSubmit={submit} noValidate>
							<label htmlFor="rs-email">Email address</label>
							<input
								id="rs-email"
								name="email"
								type="email"
								autoComplete="email"
								placeholder="you@example.com"
								required
							/>
							<label htmlFor="rs-password">Password</label>
							<input
								id="rs-password"
								name="password"
								type="password"
								autoComplete="current-password"
								placeholder="Enter your password"
								required
							/>
							{error && (
								<p className="rs-error" role="alert">
									{error}
								</p>
							)}
							<button className="rs-primary" disabled={busy}>
								{busy ? 'Signing in…' : 'Sign in to your studio'} {icon('arrow-right')}
							</button>
						</form>
					</div>
					<small>© {new Date().getFullYear()} Portfolio Studio</small>
				</section>
			</div>
		</div>
	);
}

export default function Studio() {
	const [session, setSession] = useState(null),
		[checking, setChecking] = useState(true),
		[section, setSection] = useState('overview');
	const [records, setRecords] = useState({}),
		[error, setError] = useState(''),
		[notice, setNotice] = useState(''),
		[loading, setLoading] = useState(false);
	const [editing, setEditing] = useState(null),
		[values, setValues] = useState({}),
		[fieldErrors, setFieldErrors] = useState({}),
		[busy, setBusy] = useState(false),
		[deleting, setDeleting] = useState(null);
	const canView = (key) =>
		session && (session.permissions[key]?.view || session.permissions[key]?.change);
	async function refresh(current = session) {
		setLoading(true);
		setError('');
		try {
			const keys = Object.keys(current.permissions).filter(
				(key) => current.permissions[key].view || current.permissions[key].change,
			);
			const results = await Promise.all(
				keys.map(async (key) => [key, (await api(`${key}/`)).records]),
			);
			setRecords(Object.fromEntries(results));
		} catch (e) {
			if (e.status === 401) {
				setSession(null);
				window.history.replaceState({}, '', '/login/');
			} else setError(e.message);
		} finally {
			setLoading(false);
		}
	}
	useEffect(() => {
		document.title = 'Portfolio Studio';
		api('session/')
			.then((current) => {
				setSession(current);
				window.history.replaceState({}, '', '/admin/');
				refresh(current);
			})
			.catch((e) => {
				if (e.status === 401) {
					window.history.replaceState({}, '', '/login/');
				} else setError(e.message);
			})
			.finally(() => setChecking(false));
	}, []);
	function loggedIn(current) {
		setSession(current);
		window.history.replaceState({}, '', '/admin/');
		refresh(current);
	}
	async function signOut() {
		try {
			await api('session/', 'DELETE');
			setSession(null);
			setRecords({});
			setEditing(null);
			setSection('overview');
			window.history.replaceState({}, '', '/login/');
		} catch (e) {
			setError(e.message);
		}
	}
	function choose(key) {
		setSection(key);
		setEditing(null);
		setDeleting(null);
		setNotice('');
		setError('');
	}
	function edit(record = {}) {
		setEditing(record);
		setFieldErrors({});
		setNotice('');
		setError('');
		setValues(
			Object.fromEntries(
				Object.keys(fields[section]).map((key) => [
					key,
					jsonFields.includes(key)
						? JSON.stringify(record[key] ?? (key === 'education' ? {} : []), null, 2)
						: (record[key] ?? (key === 'order' ? 0 : '')),
				]),
			),
		);
	}
	async function save(event) {
		event.preventDefault();
		if (busy) return;
		setBusy(true);
		setFieldErrors({});
		setError('');
		const data = { ...values };
		try {
			for (const key of jsonFields) {
				if (key in data) {
					try {
						data[key] = JSON.parse(data[key]);
					} catch {
						setFieldErrors({ [key]: ['Enter valid JSON.'] });
						throw new Error('Please check the JSON field.');
					}
				}
			}
			if ('order' in data) data.order = Number(data.order);
			await api(
				`${section}/${editing.id ? `${editing.id}/` : ''}`,
				editing.id ? 'PATCH' : 'POST',
				data,
			);
			setEditing(null);
			await refresh();
			setNotice('Your changes are saved.');
		} catch (e) {
			setError(e.message);
			if (e.fields) setFieldErrors(e.fields);
		} finally {
			setBusy(false);
		}
	}
	async function remove() {
		if (busy) return;
		setBusy(true);
		try {
			await api(`${section}/${deleting.id}/`, 'DELETE');
			setDeleting(null);
			await refresh();
			setNotice('Record deleted.');
		} catch (e) {
			setError(e.message);
		} finally {
			setBusy(false);
		}
	}
	async function markRead(record) {
		if (busy) return;
		setBusy(true);
		try {
			await api(`messages/${record.id}/`, 'PATCH', { is_read: !record.is_read });
			await refresh();
		} catch (e) {
			setError(e.message);
		} finally {
			setBusy(false);
		}
	}
	if (checking)
		return (
			<div className="rs-loading" role="status">
				Opening your studio…
			</div>
		);
	if (!session)
		return (
			<>
				<Login onLogin={loggedIn} />
				{error && (
					<p className="rs-error" role="alert">
						{error}
					</p>
				)}
			</>
		);
	const visibleSections = Object.keys(sections).filter((key) => key === 'overview' || canView(key));
	return (
		<div className="rs-app">
			<aside className="rs-sidebar">
				<a className="rs-logo" href="/admin/">
					sk<span>.</span>
					<small>
						PORTFOLIO
						<br />
						STUDIO
					</small>
				</a>
				<span className="rs-nav-label">YOUR WORKSPACE</span>
				<nav aria-label="Studio navigation">
					{visibleSections.map((key) => (
						<button
							key={key}
							className={section === key ? 'selected' : ''}
							onClick={() => choose(key)}
							aria-current={section === key ? 'page' : undefined}
						>
							{icon(sections[key][1])}
							{sections[key][0]}
							{key === 'messages' && (
								<span className="rs-badge">
									{(records.messages || []).filter((item) => !item.is_read).length}
								</span>
							)}
						</button>
					))}
				</nav>
				<a className="rs-view" href="/" target="_blank" rel="noopener">
					View portfolio {icon('arrow-up-right-from-square')}
				</a>
				<div className="rs-account">
					<span>{icon('user')}</span>
					<div>
						<strong>{session.user.name}</strong>
						<small>Administrator workspace</small>
					</div>
				</div>
				<button className="rs-logout" onClick={signOut}>
					{icon('arrow-right-from-bracket')} Sign out
				</button>
			</aside>
			<main className="rs-main">
				<header className="rs-topbar">
					<span>
						Workspace <span>/</span> {sections[section][0]}
					</span>
					<span>
						{new Date().toLocaleDateString(undefined, {
							month: 'short',
							day: 'numeric',
							year: 'numeric',
						})}
					</span>
				</header>
				<div className="rs-content">
					<div className="rs-page-heading">
						<div>
							<span className="rs-eyebrow">
								{section === 'overview' ? 'YOUR WORK, YOUR SPACE' : 'MAKE IT CURRENT'}
							</span>
							<h1>
								{section === 'overview' ? (
									<>
										A little maintenance.
										<br />
										<em>A lasting impression.</em>
									</>
								) : (
									sections[section][0]
								)}
							</h1>
							<p>
								{section === 'overview'
									? 'Everything you need to keep your portfolio moving forward.'
									: section === 'messages'
										? 'Conversations start here. Read and manage incoming messages.'
										: 'Update the content visitors see on your portfolio.'}
							</p>
						</div>
						{fields[section] && !editing && session.permissions[section].add && (
							<button className="rs-primary" onClick={() => edit()}>
								{icon('plus')} Add{' '}
								{section === 'projects'
									? 'project'
									: section === 'experience'
										? 'experience'
										: 'profile'}
							</button>
						)}
					</div>
					{error && (
						<div className="rs-error" role="alert">
							{error} <button onClick={() => refresh()}>Refresh</button>
						</div>
					)}
					{notice && (
						<div className="rs-success" role="status">
							{notice}
						</div>
					)}
					{loading && (
						<p role="status" className="rs-muted">
							Updating workspace…
						</p>
					)}
					{section === 'overview' && (
						<>
							<div className="rs-stats">
								{visibleSections
									.filter((key) => key !== 'overview')
									.map((key) => (
										<button key={key} onClick={() => choose(key)}>
											<span>
												{sections[key][0]} {icon(sections[key][1])}
											</span>
											<strong>
												{String(
													key === 'messages'
														? (records[key] || []).filter((item) => !item.is_read).length
														: (records[key] || []).length,
												).padStart(2, '0')}
											</strong>
											<small>
												{key === 'messages' ? 'Unread messages' : 'Published in your portfolio'}
											</small>
										</button>
									))}
							</div>
							<div className="rs-dashboard-grid">
								<section className="rs-panel">
									<h2>Your content, at a glance</h2>
									{visibleSections
										.filter((key) => key !== 'overview')
										.map((key) => (
											<button className="rs-content-row" key={key} onClick={() => choose(key)}>
												<span className="rs-row-icon">{icon(sections[key][1])}</span>
												<span>
													<strong>{sections[key][0]}</strong>
													<small>
														{key === 'projects'
															? 'Show what you have built'
															: key === 'experience'
																? 'Keep your journey up to date'
																: key === 'profile'
																	? 'Tell your story'
																	: 'Stay in touch with your visitors'}
													</small>
												</span>
												{icon('arrow-right')}
											</button>
										))}
								</section>
								{canView('messages') && (
									<section className="rs-panel">
										<h2>Latest messages</h2>
										{(records.messages || []).slice(0, 4).map((item) => (
											<button
												className="rs-message-preview"
												key={item.id}
												onClick={() => choose('messages')}
											>
												<strong>
													{item.name}
													<span>{item.is_read ? 'Read' : 'New'}</span>
												</strong>
												<p>{item.message.slice(0, 120)}</p>
												<small>{new Date(item.created_at).toLocaleDateString()}</small>
											</button>
										))}
										{!records.messages?.length && (
											<div className="rs-empty">
												{icon('envelope-open')}
												<h3>A quiet inbox.</h3>
												<p>Messages from your contact form will appear here.</p>
											</div>
										)}
									</section>
								)}
							</div>
						</>
					)}
					{section !== 'overview' && editing && (
						<form className="rs-editor rs-panel" onSubmit={save} noValidate>
							<h2>
								{editing.id ? 'Edit' : 'Add'} {sections[section][0].toLowerCase()}
							</h2>
							<div className="rs-editor-fields">
								{section === 'profile' && (
									<div className="rs-wide">
										<ProfilePhoto
											profile={editing}
											onUploaded={(result) => {
												setEditing({ ...editing, photo: result.photo });
												refresh();
											}}
										/>
									</div>
								)}
								{Object.entries(fields[section]).map(([key, label]) => (
									<div key={key} className={longFields.includes(key) ? 'rs-wide' : ''}>
										<label htmlFor={`edit-${key}`}>{label}</label>
										{longFields.includes(key) ? (
											<textarea
												id={`edit-${key}`}
												rows={jsonFields.includes(key) ? 7 : 4}
												value={values[key]}
												onChange={(e) => setValues({ ...values, [key]: e.target.value })}
												aria-invalid={Boolean(fieldErrors[key])}
												aria-describedby={fieldErrors[key] ? `err-${key}` : undefined}
											/>
										) : (
											<input
												id={`edit-${key}`}
												type={key === 'order' ? 'number' : 'text'}
												min={key === 'order' ? 0 : undefined}
												value={values[key]}
												onChange={(e) => setValues({ ...values, [key]: e.target.value })}
												aria-invalid={Boolean(fieldErrors[key])}
												aria-describedby={fieldErrors[key] ? `err-${key}` : undefined}
											/>
										)}{' '}
										{fieldErrors[key] && (
											<small className="rs-field-error" id={`err-${key}`}>
												{fieldErrors[key].join(' ')}
											</small>
										)}
									</div>
								))}
							</div>
							<div className="rs-editor-actions">
								<button className="rs-primary" disabled={busy}>
									{busy ? 'Saving…' : 'Save changes'}
								</button>
								<button
									className="rs-secondary"
									type="button"
									disabled={busy}
									onClick={() => setEditing(null)}
								>
									Cancel
								</button>
							</div>
						</form>
					)}
					{section !== 'overview' && !editing && (
						<section className="rs-panel rs-records">
							{(records[section] || []).map((record) => (
								<article key={record.id} className="rs-record">
									<div className="rs-record-body">
										<div className="rs-record-heading">
											<h2>{record.title || record.role || record.name}</h2>
											{section === 'messages' && (
												<span className={`rs-status ${record.is_read ? '' : 'new'}`}>
													{record.is_read ? 'Read' : 'New'}
												</span>
											)}
										</div>
										<span className="rs-muted">
											{record.category || record.organization || record.email}
											{record.period && ` · ${record.period}`}
										</span>
										<p>{record.message || record.description || record.summary}</p>
										{record.created_at && (
											<small className="rs-muted">
												{new Date(record.created_at).toLocaleString()}
											</small>
										)}
									</div>
									<div className="rs-record-actions">
										{session.permissions[section].change &&
											(section === 'messages' ? (
												<button
													className="rs-secondary"
													disabled={busy}
													onClick={() => markRead(record)}
												>
													{record.is_read ? 'Mark unread' : 'Mark read'}
												</button>
											) : (
												<button className="rs-secondary" onClick={() => edit(record)}>
													{icon('pen')} Edit
												</button>
											))}
										{session.permissions[section].delete && (
											<button
												className="rs-delete"
												onClick={() => {
													setDeleting(record);
													setError('');
												}}
											>
												Delete
											</button>
										)}
									</div>
									{deleting?.id === record.id && (
										<div className="rs-confirm" role="alert">
											<p>Delete this record permanently?</p>
											<button className="rs-delete" disabled={busy} onClick={remove}>
												{busy ? 'Deleting…' : 'Confirm delete'}
											</button>
											<button
												className="rs-secondary"
												disabled={busy}
												onClick={() => setDeleting(null)}
											>
												Keep record
											</button>
										</div>
									)}
								</article>
							))}
							{!loading && !records[section]?.length && (
								<div className="rs-empty">
									{icon(sections[section][1])}
									<h3>No {sections[section][0].toLowerCase()} yet.</h3>
									<p>
										{section === 'messages'
											? 'Incoming messages will appear here.'
											: 'Add your first record to get started.'}
									</p>
								</div>
							)}
						</section>
					)}
				</div>
				<footer className="rs-footer">Portfolio Studio / Make it yours.</footer>
			</main>
		</div>
	);
}
