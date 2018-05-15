#!/usr/bin/perl

use strict;
use CGI;
use MIME::Base64 qw(encode_base64);
use JSON;
use Data::Dumper;

use vars qw ($cgi);
$cgi=new CGI;

open(DEBUG, ">>debug") or die $!;

my $server_endpoint = "https://accounts.spotify.com/api/token";
my $code = $cgi->param('code');
my $redirect_uri="https://www.partyatmy.house/callback.cgi";
my $client_id=""; # your API info
my $client_secret=""; # your API info
my $encoded_payload=encode_base64("$client_id:$client_secret","");

my $json = &getToken;
my $response = decode_json($json);
die if (!&validateToken);
my $partyNumber=&createParty;

&print_html;

sub getToken {
	my $cmd="curl -H \"Authorization: Basic $encoded_payload\" ".
	"-d grant_type=authorization_code -d code=$code ".
	"-d redirect_uri=$redirect_uri https://accounts.spotify.com/api/token";

	my $res=`$cmd`;
	print DEBUG "res = $res\n";
	return $res;
}

sub validateToken {
	# just making sure everything is here
	# we don't handle errors yet, however
	if ($response->{refresh_token} && $response->{token_type} && $response->{access_token}) {
		print DEBUG "Token validated\n";
		return 1;
	}
	print DEBUG "Token no good\n";
	return 0;
}

sub createParty {
	my $partyNumber=&partyNumber;
	my $file = "/home/agustin/partyatmyhouse/parties/party.$partyNumber";
	
	if (-e $file) {
		# file exists with this number, create a new party
		&createParty;
		print DEBUG "Party $file exists.\n";
	}
	else {
	print DEBUG "Creating new party $file\n";
		open(PARTY, ">$file") or die $!;
		print PARTY "refresh_token:$response->{refresh_token}\n".
		"token_type:$response->{token_type}\n".
		"access_token:$response->{access_token}\n".
		"scope:$response->{scope}\n";
	}
	return $partyNumber;
}

	

sub partyNumber {
	my @chars = ('1'..'9');
	my $length = 4;
	my $number = '';

	for (1..$length) {
		$number .= $chars[int rand @chars];
	}

	return $number;
}

sub print_html {
        my $html='<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">'."\n".
		'<html><head><title>Party Starter</title>'.
		'<meta http-equiv="refresh" content="0; url=http://www.partyatmy.house/#/partystarted/'.$partyNumber.'" />'.
		'</head><body></body></html>';
		
        print $cgi->header;
        print $html;
        exit;
}



	
