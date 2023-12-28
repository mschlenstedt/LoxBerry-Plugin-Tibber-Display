#!/usr/bin/perl

# Copyright 2023 Michael Schlenstedt, michael@loxberry.de
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


##########################################################################
# Modules
##########################################################################

# use Config::Simple '-strict';
# use CGI::Carp qw(fatalsToBrowser);
use CGI;
use LoxBerry::System;
#use LoxBerry::IO;
use LoxBerry::JSON;
use LoxBerry::Log;
use warnings;
use strict;
#use Data::Dumper;

##########################################################################
# Variables
##########################################################################

my $log;

# Read Form
my $cgi = CGI->new;
my $q = $cgi->Vars;

my $version = LoxBerry::System::pluginversion();
my $template;

# Language Phrases
my %L;

# Globals 
my $CFGFILE = $lbpconfigdir . "/plugin.json";
my %versions;

##########################################################################
# AJAX
##########################################################################

if( $q->{ajax} ) {
	
	## Logging for ajax requests
	$log = LoxBerry::Log->new (
		name => 'AJAX',
		filename => "$lbplogdir/ajax.log",
		stderr => 1,
		loglevel => 7,
		addtime => 1,
		append => 1,
		nosession => 1,
	);
	
	LOGSTART "P$$ Ajax call: $q->{ajax}";
	LOGDEB "P$$ Request method: " . $ENV{REQUEST_METHOD};
	
	## Handle all ajax requests 
	my %response;
	ajax_header();

	# Save Settings
	if( $q->{ajax} eq "savesettings" ) {
		LOGINF "P$$ savesettings: Savesettings was called.";
		$response{error} = &savesettings();
		print JSON->new->canonical(1)->encode(\%response);
	}

	# Get config
	if( $q->{ajax} eq "getconfig" ) {
		LOGINF "P$$ getconfig: Getconfig was called.";
		my $content;
		if ( !$q->{config} ) {
			LOGINF "P$$ getconfig: No config given.";
			$response{error} = "1";
			$response{message} = "No config given";
		}
		elsif ( !-e $lbpconfigdir . "/" . $q->{config} . ".json" ) {
			LOGINF "P$$ getconfig: Config file does not exist.";
			$response{error} = "1";
			$response{message} = "Config file does not exist";
		}
		else {
			# Config
			my $cfgfile = $lbpconfigdir . "/" . $q->{config} . ".json";
			LOGINF "P$$ Parsing Config: " . $cfgfile;
			$content = LoxBerry::System::read_file("$cfgfile");
			print $content;
		}
		print JSON->new->canonical(1)->encode(\%response) if !$content;
	}

	exit;

##########################################################################
# Normal request (not AJAX)
##########################################################################

} else {
	
	require LoxBerry::Web;
	
	## Logging for serverside webif requests
	#$log = LoxBerry::Log->new (
	#	name => 'Webinterface',
	#	filename => "$lbplogdir/webinterface.log",
	#	stderr => 1,
	#	loglevel => 7,
	#	addtime => 1
	#);

	LOGSTART "Tibber-Display WebIf";
	
	# Init Template
	$template = HTML::Template->new(
	    filename => "$lbptemplatedir/settings.html",
	    global_vars => 1,
	    loop_context_vars => 1,
	    die_on_bad_params => 0,
	);
	%L = LoxBerry::System::readlanguage($template, "language.ini");
	
	# Default is LabCom form
	$q->{form} = "settings" if !$q->{form};

	if ($q->{form} eq "settings") { &form_settings() }
	elsif ($q->{form} eq "loxconfig") { &form_loxconfig() }
	elsif ($q->{form} eq "log") { &form_log() }

	# Print the form
	&form_print();
}

exit;


##########################################################################
# Form: Settings
##########################################################################

sub form_settings
{
	$template->param("FORM_SETTINGS", 1);
	return();
}


##########################################################################
# Form: LoxConfig
##########################################################################

sub form_loxconfig
{
	$template->param("FORM_LOXCONFIG", 1);
	return();
}


##########################################################################
# Form: Log
##########################################################################

sub form_log
{
	$template->param("FORM_LOG", 1);
	$template->param("LOGLIST", LoxBerry::Web::loglist_html());
	return();
}

##########################################################################
# Print Form
##########################################################################

sub form_print
{
	# Navbar
	our %navbar;

	$navbar{10}{Name} = "$L{'COMMON.LABEL_SETTINGS'}";
	$navbar{10}{URL} = 'index.cgi?form=settings';
	$navbar{10}{active} = 1 if $q->{form} eq "settings";
	
	$navbar{30}{Name} = "$L{'COMMON.LABEL_LOXCONFIG'}";
	$navbar{30}{URL} = 'index.cgi?form=loxconfig';
	$navbar{30}{active} = 1 if $q->{form} eq "loxconfig";

	$navbar{99}{Name} = "$L{'COMMON.LABEL_LOG'}";
	$navbar{99}{URL} = 'index.cgi?form=log';
	$navbar{99}{active} = 1 if $q->{form} eq "log";
	
	# Template
	LoxBerry::Web::lbheader($L{'COMMON.LABEL_PLUGINTITLE'} . " V$version", "https://wiki.loxberry.de/plugins/tibber-display/start", "");
	print $template->output();
	LoxBerry::Web::lbfooter();
	
	exit;

}


######################################################################
# AJAX functions
######################################################################

sub ajax_header
{
	print $cgi->header(
			-type => 'application/json',
			-charset => 'utf-8',
			-status => '200 OK',
	);	
}	

sub savesettings
{
	my $errors;
	my $jsonobj = LoxBerry::JSON->new();
	my $cfg = $jsonobj->open(filename => $CFGFILE);
	$cfg->{'api_key'} = $q->{'apikey'};
	$cfg->{'plot_width'} = $q->{'width'};
	$cfg->{'plot_height'} = $q->{'height'};
	$cfg->{'text_color'} = $q->{'textcolor'};
	$cfg->{'bar_color'} = $q->{'barcolor'};
	$cfg->{'bar_active_color'} = $q->{'activebarcolor'};
	$cfg->{'topic'} = $q->{'topic'};
	$jsonobj->write();
	return ($errors);
}

END {
	if($log) {
		LOGEND;
	}
}

