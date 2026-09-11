import { request } from './request';
import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import '@fortawesome/fontawesome-free/css/all.min.css';
import './styles.css';
import './redesign.css';
import ContactForm from './ContactForm';
import ErrorBoundary from './ErrorBoundary';
const Studio = React.lazy(() => import('./Studio'));

const Icon = ({ name, brand = false, ...props }) => (
	<i aria-hidden="true" className={`${brand ? 'fa-brands' : 'fa-solid'} fa-${name}`} {...props} />
);
const External = ({ href, children, ...props }) => (
	<a href={href} target="_blank" rel="noopener noreferrer" {...props}>
		{children}
	</a>
);

function ProjectArt({ index }) {
	if (index === 0)
		return (
			<div className="project-art vault" aria-hidden="true">
				<div className="art-top">
					<span>
						<Icon name="layer-group" /> StockVault
					</span>
					<span className="micro">PORTFOLIO OVERVIEW</span>
				</div>
				<div className="chart-caption">Everything in perspective.</div>
				<div className="chart">
					<svg viewBox="0 0 500 100" preserveAspectRatio="none">
						<defs>
							<linearGradient id="chartFill" x1="0" y1="0" x2="0" y2="1">
								<stop offset="0%" stopColor="#c4df88" stopOpacity=".4" />
								<stop offset="100%" stopColor="#c4df88" stopOpacity="0" />
							</linearGradient>
						</defs>
						<path
							d="M0 95 35 80 70 84 110 56 150 66 185 49 220 57 270 29 310 40 355 17 390 28 430 8 465 14 500 0 V100 H0Z"
							fill="url(#chartFill)"
						/>
						<path
							d="M0 95 35 80 70 84 110 56 150 66 185 49 220 57 270 29 310 40 355 17 390 28 430 8 465 14 500 0"
							fill="none"
							stroke="#c4df88"
							strokeWidth="2"
						/>
					</svg>
				</div>
				<div className="art-bottom">
					<span>SECURE BY DESIGN</span>
					<Icon name="lock" />
				</div>
			</div>
		);
	if (index === 1)
		return (
			<div className="project-art exam" aria-hidden="true">
				<div className="exam-sheet">
					<div className="sheet-label">
						<Icon name="graduation-cap" /> ENTRANCE PREP <span>01 / 10</span>
					</div>
					<h4>
						A little practice.
						<br />A bigger possibility.
					</h4>
					<div className="answer">
						<span>A</span> Learn the fundamentals
					</div>
					<div className="answer selected">
						<span>B</span> Put knowledge into practice
						<Icon name="check" />
					</div>
					<div className="answer">
						<span>C</span> Track your progress
					</div>
				</div>
			</div>
		);
	return (
		<div className="project-art starter" aria-hidden="true">
			<div className="terminal-bar">
				<span />
				<span />
				<span />
				<small>django-production / terminal</small>
			</div>
			<div className="terminal-code">
				<p>
					<b>~</b> docker compose up --build
				</p>
				<p className="muted-code">Starting something great.</p>
				<p>
					<span>✓</span> Database connected
				</p>
				<p>
					<span>✓</span> Authentication ready
				</p>
				<p>
					<span>✓</span> API running <span className="cursor" />
				</p>
			</div>
			<div className="terminal-python">{'{ }'}</div>
		</div>
	);
}

function experiencePoints(description) {
	const lines = description
		.split(/\r?\n/)
		.map((line) => line.trim())
		.filter(Boolean);
	const points = lines.length > 1 ? lines : (lines[0] || '').split(/(?<=[.!?])\s+(?=[A-Z])/);
	return points
		.map((point) => point.replace(/^(?:[-*•]\s+|\d+[.)]\s+)/, '').trim())
		.filter(Boolean);
}

function App() {
	const [data, setData] = useState(null),
		[error, setError] = useState(false),
		[menu, setMenu] = useState(false),
		[active, setActive] = useState('home');
	const load = () => {
		setError(false);
		request('/api/portfolio/')
			.then((r) => {
				if (!r.ok) throw Error();
				return r.json();
			})
			.then(setData)
			.catch(() => setError(true));
	};
	useEffect(load, []);
	useEffect(() => {
		if (!data) return;
		const observer = new IntersectionObserver(
			(entries) =>
				entries.forEach((e) => {
					if (e.isIntersecting) setActive(e.target.id);
				}),
			{ rootMargin: '-15% 0px -65% 0px' },
		);
		document.querySelectorAll('main > section[id]').forEach((el) => observer.observe(el));
		return () => observer.disconnect();
	}, [data]);
	useEffect(() => {
		const close = (e) => {
			if (e.key === 'Escape') setMenu(false);
		};
		window.addEventListener('keydown', close);
		return () => window.removeEventListener('keydown', close);
	}, []);
	if (!data)
		return (
			<div className="load-screen">
				<a className="wordmark" href="/">
					santosh<span>.</span>
				</a>
				<p role="status">
					{error ? 'The portfolio is temporarily unavailable.' : 'Opening the portfolio…'}
				</p>
				{error && (
					<button className="button dark" onClick={load}>
						Try again <Icon name="rotate-right" />
					</button>
				)}
			</div>
		);
	const { profile: p, projects, experience } = data;
	return (
		<>
			<a href="#main" className="skip-link">
				Skip to content
			</a>
			<header>
				<div className="container nav">
					<a className="wordmark" href="#home" onClick={() => setMenu(false)}>
						santosh<span>.</span>
					</a>
					<button
						className="menu-toggle"
						aria-expanded={menu}
						aria-controls="navigation"
						aria-label={menu ? 'Close navigation' : 'Open navigation'}
						onClick={() => setMenu(!menu)}
					>
						<Icon name={menu ? 'xmark' : 'bars'} />
					</button>
					<nav id="navigation" className={menu ? 'is-open' : ''} aria-label="Main navigation">
						{[
							['work', 'Work'],
							['about', 'About'],
							['experience', 'Experience'],
						].map(([id, label]) => (
							<a
								key={id}
								className={active === id ? 'active' : ''}
								href={`#${id}`}
								onClick={() => setMenu(false)}
							>
								{label}
							</a>
						))}
						<a href="#contact" className="nav-contact" onClick={() => setMenu(false)}>
							Let’s talk <Icon name="arrow-up-right-from-square" />
						</a>
					</nav>
				</div>
			</header>
			<main id="main">
				<section className="hero" id="home">
					<div className="container">
						<div className="hero-top">
							<span className="hero-edition">
								PORTFOLIO <span>/</span> SANTOSH KARKI
							</span>
							<span className="location">
								<Icon name="location-dot" /> {p.location}
							</span>
						</div>
						<div className="hero-grid">
							<div className="hero-copy">
								<div className="hero-kicker">
									<span /> BUILT WITH PURPOSE
								</div>
								<h1>
									Behind every
									<br />
									great idea.
									<br />
									<span className="serif accent">A solid backend.</span>
								</h1>
								<div className="hero-description">
									<span className="intro-line" />
									<p>
										I’m <strong>{p.name}</strong>.<br />I build the backends that bring ideas to
										life —<br className="desktop-break" /> clean APIs, secure systems, and room to
										grow.
									</p>
								</div>
								<div className="hero-actions">
									<a className="button dark" href="#work">
										Explore my work <Icon name="arrow-down" />
									</a>
									<a className="text-link" href="/resume/">
										Download CV <Icon name="download" />
									</a>
								</div>
							</div>
							<figure className="hero-portrait">
								<span className="portrait-orbit" aria-hidden="true" />
								<span className="portrait-code" aria-hidden="true">
									&lt;/&gt;
								</span>
								<div className="portrait-frame">
									<img
										src={p.photo_url || '/santosh-karki.jpg'}
										alt={p.name}
										width="400"
										height="400"
										fetchPriority="high"
									/>
								</div>
								<figcaption>
									<span>{p.name}</span>
									<span>Backend Developer</span>
								</figcaption>
								<div className="portrait-note" aria-hidden="true">
									<Icon name="code" />
									<span>
										Thoughtful architecture.
										<br />
										Reliable execution.
									</span>
								</div>
							</figure>
						</div>
						<div className="hero-footer">
							<span>
								BACKEND ENGINEERING <span className="tiny-cross">/</span> CONTINUOUS LEARNING
							</span>
							<span className="hero-signature">Code with intention. Build with care.</span>
						</div>
					</div>
				</section>
				<div className="stack-strip">
					<div className="container">
						<span className="stack-label">MY EVERYDAY TOOLKIT</span>
						<span>
							<Icon name="python" brand /> Python
						</span>
						<span className="django-word">django</span>
						<span>
							<Icon name="bolt" /> FastAPI
						</span>
						<span>
							<Icon name="database" /> PostgreSQL
						</span>
						<span>
							<Icon name="docker" brand /> Docker
						</span>
						<span>
							<Icon name="git-alt" brand /> Git
						</span>
					</div>
				</div>
				<section id="work" className="container section work">
					<div className="section-heading">
						<div>
							<span className="eyebrow section-index">01 / SELECTED WORK</span>
							<h2>
								Less talk.
								<br />
								<span className="serif">More building.</span>
							</h2>
							<p className="section-intro">
								A selection of backends, tools, and ideas brought to life.
							</p>
						</div>
						<div className="work-overview">
							<div className="work-count">
								<strong>{String(projects.length).padStart(2, '0')}</strong>
								<span>
									PROJECTS
									<br />
									BUILT WITH PURPOSE
								</span>
							</div>
							<p>
								Secure APIs, practical developer tools, and platforms that make complex workflows
								simpler.
							</p>
							<External className="text-link" href={p.github}>
								All repositories <Icon name="arrow-up-right-from-square" />
							</External>
						</div>
					</div>
					<div className="project-grid">
						{projects.slice(0, 3).map((project, index) => (
							<External
								href={project.url}
								className={`project-card project-${index}`}
								key={project.id}
								aria-label={`View ${project.title} on GitHub`}
							>
								<ProjectArt index={index} />
								<div className="project-info">
									<div className="project-kicker">
										<span>{project.category}</span>
										<span>0{index + 1}</span>
									</div>
									<h3>
										{project.title}
										<Icon name="arrow-up-right-from-square" />
									</h3>
									<p>{project.description}</p>
									<div className="tags">
										{project.tags.map((tag) => (
											<span key={tag}>{tag}</span>
										))}
									</div>
									<span className="project-action">
										Explore repository <Icon name="arrow-right" />
									</span>
								</div>
							</External>
						))}
					</div>
					<div className="more-projects">
						{projects.slice(3).map((project) => (
							<External href={project.url} className="compact-project" key={project.id}>
								<div className="compact-icon">
									<Icon name={project.title === 'nppy' ? 'cube' : 'link'} />
								</div>
								<div>
									<span className="project-kicker">{project.category}</span>
									<h3>{project.title}</h3>
									<p>{project.description}</p>
								</div>
								<Icon name="arrow-up-right-from-square" />
							</External>
						))}
					</div>
				</section>
				<section id="about" className="about-section">
					<div className="container section about-grid">
						<div>
							<span className="eyebrow section-index">02 / A LITTLE ABOUT ME</span>
							<h2>
								Curious by nature.
								<br />
								<span className="serif">Backend by choice.</span>
							</h2>
							<p className="about-lead">{p.summary}</p>
							<p>
								Beyond building software, I teach programming and help students turn complex
								problems into clear, practical solutions.
							</p>
							<div className="education">
								<Icon name="graduation-cap" />
								<div>
									<strong>
										{p.education.degree} ({p.education.short})
									</strong>
									<span>
										{p.education.institution} <span className="education-divider">/</span>{' '}
										{p.education.period}
									</span>
								</div>
							</div>
						</div>
						<div className="skills">
							{p.skills.map((group) => (
								<div className="skill-group" key={group.label}>
									<div className="skill-heading">
										<Icon name={group.icon} />
										<h3>{group.label}</h3>
									</div>
									<div className="skill-items">
										{group.items.map((item) => (
											<span key={item}>{item}</span>
										))}
									</div>
								</div>
							))}
						</div>
					</div>
				</section>
				<section id="experience" className="container section experience-grid">
					<div>
						<span className="eyebrow section-index">03 / THE JOURNEY</span>
						<h2>
							Building.
							<br />
							Teaching.
							<br />
							<span className="serif">Always learning.</span>
						</h2>
						<div className="journey-context">
							<p>
								From developing recruitment APIs to teaching programming, I turn complex problems
								into practical solutions.
							</p>
							<div className="journey-focus">
								<span>
									<Icon name="code" />
								</span>
								<div>
									<strong>Build with clarity</strong>
									<p>Secure authentication, dependable APIs, and thoughtful backend validation.</p>
								</div>
							</div>
							<div className="journey-focus">
								<span>
									<Icon name="graduation-cap" />
								</span>
								<div>
									<strong>Share what you learn</strong>
									<p>
										Programming fundamentals, analytical thinking, and hands-on problem solving.
									</p>
								</div>
							</div>
						</div>
					</div>
					<div className="timeline" aria-label="Professional experience timeline">
						{experience.map((job, index) => (
							<article className="job" key={job.id}>
								<span
									className={`timeline-dot ${index === 0 ? 'current' : ''}`}
									aria-hidden="true"
								/>
								<div className="job-meta">
									<span>{job.period}</span>
								</div>
								<h3>{job.role}</h3>
								<div className="organization">
									{job.organization}
									<span>{job.location}</span>
								</div>
								<ul className="job-points">
									{experiencePoints(job.description).map((point, index) => (
										<li key={index}>{point}</li>
									))}
								</ul>
							</article>
						))}
					</div>
				</section>
				<section id="contact" className="contact-section">
					<div className="container">
						<div className="contact-top">
							<span className="eyebrow">04 / LET’S CONNECT</span>
						</div>
						<div className="contact-main">
							<div>
								<h2>
									Have something
									<br />
									<span className="serif">in mind?</span>
								</h2>
								<p>
									A project, an opportunity, or a good conversation.
									<br />
									I’d love to hear from you.
								</p>
							</div>
							<ContactForm />
						</div>
						<div className="contact-bottom">
							<a className="email-link" href={`mailto:${p.email}`}>
								{p.email}
								<Icon name="arrow-up-right-from-square" />
							</a>
							<div className="socials">
								<External href={p.github}>
									<Icon name="github" brand /> GitHub
								</External>
								<External href={p.linkedin}>
									<Icon name="linkedin-in" brand /> LinkedIn
								</External>
								<a href={`tel:${p.phone}`}>
									<Icon name="phone" /> {p.phone}
								</a>
							</div>
						</div>
					</div>
				</section>
			</main>
			<footer className="container footer">
				<span>
					© {new Date().getFullYear()} {p.name}
				</span>
			</footer>
		</>
	);
}
const isStudio = /^\/(admin|login)(\/|$)/.test(window.location.pathname);
createRoot(document.getElementById('root')).render(
	<ErrorBoundary>
		<React.Suspense
			fallback={
				<div className="load-screen" role="status">
					Loading…
				</div>
			}
		>
			{isStudio ? <Studio /> : <App />}
		</React.Suspense>
	</ErrorBoundary>,
);
