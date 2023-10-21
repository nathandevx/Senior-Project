from django.shortcuts import render, redirect
from django.contrib import messages
from senior_project.utils import superuser_required
from home.models import Configurations
from home.forms import ConfigurationForm


@superuser_required
def config_create(request):
	# If a config already exists, redirect to the read url.
	if Configurations.config_exists():
		messages.info(request, f'Only one configuration is allowed, and it already exists.')
		return redirect(Configurations.get_first_configuration().get_read_url())
	else:  # Otherwise, let them create one.
		if request.method == 'POST':
			form = ConfigurationForm(request.POST)
			if form.is_valid():
				configuration = form.save()
				return redirect(configuration.get_read_url())
		else:
			form = ConfigurationForm()
		return render(request, 'home/config/create.html', {'form': form})


@superuser_required
def config_read(request, pk):
	# If config exists, allow them to read it
	if Configurations.config_exists():
		config = Configurations.get_first_configuration()
		return render(request, 'home/config/read.html', {'config': config})
	else:  # Otherwise, redirect them to create one
		return redirect(Configurations.get_create_url())


@superuser_required
def config_update(request, pk):
	# If no config exists, redirect them to create one.
	if not Configurations.config_exists():
		return redirect(Configurations.get_create_url())
	else:  # Otherwise, allow them to update the config
		config = Configurations.get_first_configuration()
		if request.method == 'POST':
			form = ConfigurationForm(request.POST, instance=config)
			if form.is_valid():
				config = form.save()
				return redirect(config.get_read_url())
		else:
			form = ConfigurationForm(instance=config)
		return render(request, 'home/config/update.html', {'config': config, 'form': form})
