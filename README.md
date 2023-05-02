# Pastry Bites: Pastry Ordering Website

![Project logo](static/images/README/logo.jpg)

## Quick Links
- [Introduction](#introduction)
- [The Client](#the-client)
- [The Team](#the-team)
- [Features](#features)
- [Technologies](#technologies)
- [Testing](#testing)
- [Developer Instructions](#developer-instructions)
- [Project Images](#project-images)
  - [JIRA roadmap (part of it)](#jira-roadmap-part-of-it)
  - [Sign up page](#sign-up-page)
  - [Login page](#login-page)
  - [Profile page](#profile-page)
  - [Manage registered emails page](#manage-registered-emails)
  - [Admin page](#admin-page)

## Introduction
- Sacramento State CSC [190](https://catalog.csus.edu/search/?P=CSC%20190)-[191](https://catalog.csus.edu/search/?P=CSC%20191) Senior Project.
- Pastry Bites is a website that allows customers to order and pay for pastries, while providing a user-friendly interface for managing orders and generating reports for the client (admin).

## The Client
- Cigdem Askin is an individual who is interested in a website that will help her keep manage and track orders she receives. 
- Prior to the website's creation, Cigdem managed orders and customer data using Excel, a process that was both time-consuming and error-prone. Our website now streamlines these tasks by providing real-time order notifications, efficient tracking, secure payments, and data analysis through charts and graphs.

## The Team
- [Muhammad Ahmed](https://github.com/mahmed5499)
- [Jordan Huang](https://github.com/jordanhuang916)
- [Nathan Martinez](https://github.com/nathandevx)
- [Tiffany Nguyen](https://github.com/tiffanypnguyen)
- [Jainish Sanjaykumar Patel](https://github.com/jainish123-pixel)
- [Rahil Patel](https://github.com/rahilpatel29)
- [Moises Vaca](https://github.com/B1ueF10WER)
- [Lovedeep Vasisht](https://github.com/LovedeepVasisht)

## Features
- The admin (client) is able to create, view, filter, and export reports on past orders. They'll be able to view how many orders they've received over a given time period on a graph. 
- Visitors can browse for pastries and eventually register if they'd like to purchase some. 
- Users can change their account information and view previous orders.
- Add to cart feature so users can add multiple items to their cart.
- Checkout and order form so users can enter their information (address, phone number, etc) to purchase the order.
- **User authentication**: Users can register and log in to the website. 
- **User authorization**: We created three user groups to manage access to different sections of the website: visitors, logged in users, and admins. Each group has different levels of access and permissions:
   - **Visitors**: They can view the website, but they're not able to place orders.
   - **Logged-in Users**: In addition to the features available to visitors, logged-in users can place and pay for orders, view their order history, and manage their account settings.
   - **Admins**: Admins have full access to the platform, including an admin dashboard for managing orders, generating reports, and exporting data for further analysis. They can also manage other users and change site settings.

## Technologies
- **Python**: The programming language used to build the backend functionality of the website.
- **Django**: The web framework that provides the tools for creating websites in Python.
- **HTML/CSS**: For structuring and styling the website.
- **JavaScript**: Adds extra interactivity and client side activity (asynchronous calls) to the website.
- **Bootstrap**: For creating responsive and modern UIs.
- **Stripe**: For handling payments securely and maintaining [PCI compliance](https://stripe.com/guides/pci-compliance).
- **AWS S3**: For handling uploaded media (such as product images, generated reports, etc). 
- **Google Maps Embed API**: For showing where the client is located.
- **Heroku PostgreSQL**: For hosting the database.
- **Heroku**: For deploying and hosting the web application.

## Testing
- When the web application is finished, it will have tests for user account creation, checkout page, payments, order tracking, emails, etc.
- We will use Django's builtin tester for unit tests and selenium for integration tests.

## Deployment
- The application will be deployed using Heroku. It will be accessible to anyone with a link.
- For now, see the [developer instructions](#developer-instructions) on how to run the application on your local machine.

## Developer Instructions
- This guide is meant for installing and running the site on Windows OS but with minor tweaks it should work on other OS's like Mac and Linux.
- **Install Python**: Download the latest version of Python (or preferably v3.10) from the [official website](https://www.python.org/downloads/). During the installation process, check the option "Add Python to PATH" to make Python accessible from the command line.
- **Install Git**: Download it at their [official website](https://git-scm.com/downloads).
  - **Clone the Repository**: Open the command prompt and navigate to the folder you want to download the project. Run this command without the quotes "git clone https://github.com/CSC190SeniorProject/SeniorProject"
- **Alternative to using Git**: Alternatively, you can download the ZIP file from the [repository page](https://github.com/CSC190SeniorProject/SeniorProject). 
- **Running the site**:
  - Navigate to the project folder via the terminal by running "cd SeniorProject". You should be in the directory that the "README.md" file is in.
  - Setting up the Python virtual environment
    - Create it by running "python -m venv venv".
    - Activate it by running "venv\Scripts\activate".
  - Install the dependencies by running "pip install -r requirements.txt"
  - Set up the database by running "python manage.py migrate"
  - Finally, run the development server by running "python manage.py runserver". It will output a link where you can view the project.

## Project images
- The pages are still in progress and the design has not been finalized yet. We will continue to add more pages and make improvements to them during CSC 191.
- The first image is part of our JIRA roadmap. It shows when we expect certain features to be done. The other images relate to the project.

## JIRA roadmap (part of it)
![part of our JIRA roadmap](static/images/README/roadmap.PNG)

### Sign up page
![sign up page](static/images/README/register_page.PNG)

### Login page
![login page](static/images/README/login_page.PNG)

### Profile page
![profile page](static/images/README/profile_page.PNG)

### Manage registered emails
![manage registered emails page](static/images/README/manage_emails_page.PNG)

### Admin page
![admin page](static/images/README/admin_page.PNG)

