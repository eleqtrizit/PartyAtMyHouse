#!/usr/bin/perl

use strict;
use CGI;
use JSON;
use Data::Dumper;

use vars qw ($cgi);
$cgi=new CGI;

open(DEBUG, ">>debug") or die $!;

my $track=$cgi->param('track');
my $partyID=$cgi->param('partyID');
my $artistID=$cgi->param('artistID');

# make sure nothing nefarious is getting passed, due to use using CURL below instead
# of something reasonable.
unless ($partyID =~ /^\d+$/) { 
	exit;
}

system("/home/agustin/partyatmyhouse/callback.cgi $partyID >>/home/agustin/partyatmyhouse/debug");

my $partyFile="/home/agustin/partyatmyhouse/parties/party.$partyID";

print DEBUG $partyFile."\n";
print DEBUG $track."\n";

my %partyConfig = &parsePartyFile;


my $addTrackCMD = 'curl -i -X POST '.
'"https://api.spotify.com/v1/users/' . $partyConfig{id} . '/playlists/' . $partyConfig{pl_id} . '/tracks?uris=' . $track . '" '.
'-H "Authorization: Bearer '. $partyConfig{access_token} . '" -H "Accept: application/json"';
print DEBUG $addTrackCMD;

my $json=`$addTrackCMD`;
print DEBUG Dumper($json);

my $callback;

if ($artistID) {
	$callback="http://www.partyatmy.house/#/songsbyartist/$artistID";
}
else {
	$callback="http://www.partyatmy.house/#/songsearch";
}

print $cgi->redirect($callback);


sub parsePartyFile {
	## there might be two keys of the same name
	# this is because they get updated after an hour
	# this will just erase the old value with the newer once at the bottom
	my %partyConfig;
	open(IN, $partyFile) or die $!;
	while(<IN>) {
		chomp($_);
		my ($param,$data) = split(/:/, $_);
		$partyConfig{$param}=$data;
	}
	close(IN);
	
	return %partyConfig;
}

	
