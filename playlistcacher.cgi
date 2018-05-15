#!/usr/bin/perl

use strict;
use CGI qw(:standard);
use JSON;
use Data::Dumper;

my $install_dir = '/home/agustin';

use vars qw ($cgi);
$cgi=new CGI;

open(DEBUG, ">>debug") or die $!;

my $partyID=$cgi->param('partyID');

system("$install_dir/partyatmyhouse/callback.cgi $partyID >> $install_dir/partyatmyhouse/debug");

my $partyFile="$install_dir/partyatmyhouse/parties/party.$partyID";

print DEBUG $partyFile."\n";

my %partyConfig = &parsePartyFile;

my $playlistCMD = 'curl -X GET "https://api.spotify.com/v1/users/' . $partyConfig{id} . '/playlists/'. $partyConfig{pl_id} .'/tracks"'.
' -H "Authorization: Bearer '. $partyConfig{access_token} . '" -s';

print DEBUG $playlistCMD."\n\n";

my $json=`$playlistCMD`;
print DEBUG $json;

## just relay the request
print header('application/json');
print $json;


sub parsePartyFile {
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

	
