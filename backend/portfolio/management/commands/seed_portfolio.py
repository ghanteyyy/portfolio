from django.core.management.base import BaseCommand

from portfolio.models import Experience, Profile, Project


class Command(BaseCommand):
	help = "Load CV content once, preserving later admin edits."

	def handle(self, *args, **options):
		Profile.objects.get_or_create(
			pk=1,
			defaults={
				"name": "Santosh Kumar Karki",
				"role": "Python Backend Developer",
				"summary": "I build dependable backends with Python, Django, and FastAPI. From secure authentication to thoughtfully structured APIs, I care about the details that make software work.",
				"email": "santoshkumarkarki2055@gmail.com",
				"phone": "+977-9861968701",
				"location": "Kathmandu, Nepal",
				"github": "https://github.com/ghanteyyy",
				"linkedin": "https://www.linkedin.com/in/santosh-kumar-karki",
				"skills": [
					{
						"label": "Languages",
						"icon": "code",
						"items": ["Python", "SQL", "JavaScript", "C"],
					},
					{
						"label": "Backend & APIs",
						"icon": "server",
						"items": ["Django", "Django REST Framework", "FastAPI", "REST APIs"],
					},
					{
						"label": "Data & security",
						"icon": "database",
						"items": [
							"PostgreSQL",
							"MySQL",
							"JWT",
							"SimpleJWT",
							"Authentication & Authorization",
						],
					},
					{
						"label": "Tools & workflow",
						"icon": "terminal",
						"items": ["Git", "GitHub", "Docker", "Docker Compose"],
					},
				],
				"education": {
					"degree": "Bachelor of Computer Application",
					"short": "BCA",
					"institution": "Tribhuvan University",
					"period": "2020 — 2025",
				},
			},
		)
		projects = [
			(
				"StockVault",
				"Portfolio management",
				"A secure foundation for personal stock portfolios. User-specific resources, protected REST endpoints, and JWT authentication.",
				["Python", "Django", "DRF", "JWT"],
				"StockVault",
			),
			(
				"Online Entrance Preparation",
				"Education platform",
				"An examination backend that brings authentication, quizzes, automated scoring, and result tracking into one platform.",
				["Django", "PostgreSQL"],
				"Online-Entrance-Preparation-Backend",
			),
			(
				"Django Production Starter",
				"Developer tooling",
				"A reusable Django starting point with REST APIs, JWT authentication using secure HttpOnly cookies, and a Docker-based setup.",
				["Django", "DRF", "JWT", "Docker"],
				"django_prod_strater",
			),
			(
				"URL Shortener",
				"API service",
				"A focused FastAPI service for creating short links and reliably redirecting visitors to their original destinations.",
				["Python", "FastAPI", "REST APIs"],
				"URL-Shortner",
			),
			(
				"nppy",
				"Python library",
				"A reusable utility library that keeps Python code modular and simplifies common development tasks.",
				["Python"],
				"nppy",
			),
		]
		for order, (title, category, description, tags, repo) in enumerate(projects):
			Project.objects.get_or_create(
				title=title,
				defaults={
					"category": category,
					"description": description,
					"tags": tags,
					"url": f"https://github.com/ghanteyyy/{repo}",
					"order": order,
				},
			)
		roles = [
			(
				"Lecturer",
				"Arunima College",
				"Bauddha, Kathmandu, Nepal",
				"2025 — Present",
				"Teaching C Programming and Operation Research to undergraduate students. Mentoring students in programming fundamentals, analytical thinking, debugging, and problem solving.",
			),
			(
				"Backend Developer Intern",
				"Nepal Oil Corporation",
				"Lokanthali, Bhaktapur, Nepal",
				"Nov 2024 — Feb 2025",
				"Developed REST APIs for job postings, candidate applications, resume uploads, and shortlisting. Implemented validation and authentication, handled candidate data securely, and collaborated with frontend developers on API integration.",
			),
		]
		for order, (role, organization, location, period, description) in enumerate(roles):
			Experience.objects.get_or_create(
				role=role,
				organization=organization,
				defaults={
					"location": location,
					"period": period,
					"description": description,
					"order": order,
				},
			)
		self.stdout.write(self.style.SUCCESS("Portfolio content is ready."))
