#!/usr/bin/perl

use strict;
use CGI;
use JSON;
use Data::Dumper;

my $install_dir = '/home/agustin';

use vars qw ($cgi);
$cgi=new CGI;

open(DEBUG, ">>$install_dir/partyatmyhouse/debug") or die $!;

my $partyID=$cgi->param('partyID');
my $partyFile="$install_dir/partyatmyhouse/parties/party.$partyID";
print DEBUG "Party Validation: $partyFile\n";

print $cgi->header;
if (-e $partyFile) {
	print DEBUG "Party Validated?: true\n";
	print "true";	
}
else {
	print DEBUG "Party Validated?: false\n";
	print "false";
}



