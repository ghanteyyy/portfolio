from django.db import models


class ContactMessage(models.Model):
	name = models.CharField(max_length=120)
	email = models.EmailField()
	message = models.TextField(max_length=5000)
	created_at = models.DateTimeField(auto_now_add=True)
	is_read = models.BooleanField(default=False)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.name} — {self.email}"


class Profile(models.Model):
	photo = models.FileField(upload_to="portraits/", blank=True)
	name = models.CharField(max_length=120)
	role = models.CharField(max_length=150)
	summary = models.TextField()
	email = models.EmailField()
	phone = models.CharField(max_length=30)
	location = models.CharField(max_length=120)
	github = models.URLField()
	linkedin = models.URLField()
	skills = models.JSONField(default=list)
	education = models.JSONField(default=dict)

	def __str__(self):
		return self.name


class Project(models.Model):
	title = models.CharField(max_length=150, unique=True)
	category = models.CharField(max_length=100)
	description = models.TextField()
	tags = models.JSONField(default=list)
	url = models.URLField()
	order = models.PositiveIntegerField(default=0)

	class Meta:
		ordering = ["order", "id"]

	def __str__(self):
		return self.title


class Experience(models.Model):
	role = models.CharField(max_length=150)
	organization = models.CharField(max_length=150)
	location = models.CharField(max_length=150)
	period = models.CharField(max_length=100)
	description = models.TextField()
	order = models.PositiveIntegerField(default=0)

	class Meta:
		ordering = ["order", "id"]

	def __str__(self):
		return f"{self.role} — {self.organization}"
