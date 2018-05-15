#!/usr/bin/perl

use strict;
use CGI;
use MIME::Base64 qw(encode_base64);
use JSON;
use Data::Dumper;

use vars qw ($cgi);
$cgi=new CGI;

my $partyNumber = $ARGV[0] || 0;


# make sure nothing nefarious is getting passed, due to use using CURL below instead
# of something reasonable.
unless ($partyNumber =~ /^\d+$/) {
        exit;
}

open(DEBUG, ">>/home/agustin/partyatmyhouse/debug") or die $!;

my $server_endpoint = "https://accounts.spotify.com/api/token";
my $code = $cgi->param('code');
my $redirect_uri="https://www.partyatmy.house/callback.cgi";
my $client_id="94b828f5ae5f4e448c44bba8c18b1f38";
my $client_secret="67cb522c6b8b448783465287acb5c513";
my $encoded_payload=encode_base64("$client_id:$client_secret","");

my $json;
my %tokens;

if ($partyNumber>0) {
	open(IN, "parties/party.$partyNumber") or die $!;
	while(<IN>) {
		chomp($_);
		my ($param,$val)=split(/:/, $_);
		$tokens{$param}=$val;
	}
	close(IN);

	if ($tokens{expires_at} < time() ) {
		&refreshToken($tokens{refresh_token});
	}
	else {
		print DEBUG "\n\nToken is still good!\n";
		exit;
	}
}
else {
	&createParty;
}


my $callback="http://www.partyatmy.house/#/partystarted/$partyNumber";
print $cgi->redirect($callback);

sub getToken {
	my $cmd="curl -H \"Authorization: Basic $encoded_payload\" ".
	"-d grant_type=authorization_code -d code=$code ".
	"-d redirect_uri=$redirect_uri https://accounts.spotify.com/api/token";

	my $res=`$cmd`;
	print DEBUG "res = $res\n";
	return $res;
}


sub refreshToken {
	my $refresh_token=shift;

	print DEBUG "Refreshing token with $refresh_token\n";

	my $file = "/home/agustin/partyatmyhouse/parties/party.$partyNumber";

	my $cmd=`curl -H \"Authorization: Basic $encoded_payload\" ".
	"-d grant_type=refresh_token -d refresh_token=$refresh_token ".
	"-d redirect_uri=$redirect_uri https://accounts.spotify.com/api/token`;

	my $json=`$cmd`;
	open(PARTY, ">>$file") or die $!;

	print DEBUG "\n\nCMD: $cmd \n\nDUMPER: ";
        print DEBUG Dumper($json);

        my $response=decode_json($json);
	print DEBUG "$response\n";

        my $expires_at = time() + $response->{expires_in};
	print DEBUG  "\nrefresh_token:$response->{refresh_token}\n".
	"access_token:$response->{access_token}\n".
	"expires_at:$expires_at\n";
	
	print PARTY "refresh_token:$response->{refresh_token}\n".
        "access_token:$response->{access_token}\n".
        "expires_at:$expires_at\n";
	close(PARTY);
}

## this sub isn't being used at the moment
sub validateToken {

	my %response;
	# just making sure everything is here
	# we don't handle errors yet, however
	#if ($response->{refresh_token} && $response->{token_type} && $response->{access_token}) {
	#	print DEBUG "Token validated\n";
	#	return 1;
	#}
	print DEBUG "Token no good\n";
	return 0;
}

sub createParty {
	my $file;
	$partyNumber=&partyNumber;
	$file = "/home/agustin/partyatmyhouse/parties/party.$partyNumber";
	if (-e $file) {
                # file exists with this number, create a new party
                &createParty;
       	}
	print DEBUG "Creating party $file\n";
	
	$json = &getToken;
	my $response = decode_json($json);
	

	if (1==1) {
		open(PARTY, ">$file") or die $!;
		
		$json = `curl -X GET https://api.spotify.com/v1/me -H "Authorization: Bearer $response->{access_token}"`;
		print DEBUG Dumper($json);
		
		my $user_details=decode_json($json);
		
		my $expires_at = time() + $response->{expires_in};

		print PARTY "refresh_token:$response->{refresh_token}\n".
        	"token_type:$response->{token_type}\n".
        	"access_token:$response->{access_token}\n".
        	"expires_at:$expires_at\n".
        	"scope:$response->{scope}\n".
        	"id:$user_details->{id}\n".
        	"url:$user_details->{url}\n".
        	"uri:$user_details->{uri}\n".
        	"display_name:$user_details->{display_name}\n";

		my $createPlaylistCMD = 'curl -X POST "https://api.spotify.com/v1/users/' . $user_details->{id}. '/playlists" '.
		'-H "Authorization: Bearer '. $response->{access_token}. '" '.
		'-H "Content-Type: application/json" --data "{\"name\":\"PartyAtMyHouse\", \"public\":true}"';
		
		print DEBUG $createPlaylistCMD."\n";
		
		$json = `$createPlaylistCMD`;
		print DEBUG Dumper($json);
		
		my $playlist = decode_json($json);
		
		print PARTY "pl_name:$playlist->{name}\n".
		"pl_href:$playlist->{href}\n".
		"pl_uri:$playlist->{uri}\n".
		"pl_id:$playlist->{id}\n";
		
		
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


	
