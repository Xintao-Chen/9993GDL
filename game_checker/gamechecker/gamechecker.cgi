#!/usr/bin/perl -w -U

$| = 1; # autoflush output

# server process that reads GDL game descriptions and checks them for errors

use CGI;
use File::Temp;
use strict;

my $gdl = <<GDL;
(role player)

(init f)

(<= (legal player a)
	(true f)
)

(<= (next g)
	(does player a))

(<= terminal
	(true g)
)

(<=	(goal player 100)
	(true g)
)
GDL
my $run_simulations_time = 0;
my $run_dfs_time = 0;
my $gdl_version = 1;

sub trim{
# Leerzeichen am Anfang und Ende des Strings entfernen
	my $s=$_[0];
	$s=~s/^\s+//;
	$s=~s/\s+$//;
	return $s;
}

sub parse_query { # ($query)
	my $query = $_[0];
	
	if(defined($query->param('gdl'))) {
		$gdl = $query->param('gdl');
	}
	if(defined($query->param('run_simulations_time'))) {
		$run_simulations_time = $query->param('run_simulations_time');
	}
	$run_simulations_time = int($run_simulations_time);
	if ($run_simulations_time>600) {
		$run_simulations_time=600;
	}
	if ($run_simulations_time<0) {
		$run_simulations_time=0;
	}
	if(defined($query->param('run_dfs_time'))) {
		$run_dfs_time = $query->param('run_dfs_time');
	}
	$run_dfs_time = int($run_dfs_time);
	if ($run_dfs_time>600) {
		$run_dfs_time=600;
	}
	if ($run_dfs_time<0) {
		$run_dfs_time=0;
	}
	if(defined($query->param('gdl_version'))) {
		$gdl_version = $query->param('gdl_version');
	}
	$gdl_version = int($gdl_version);
	if ($gdl_version>2) {
		$gdl_version=2;
	}
	if ($gdl_version<1) {
		$gdl_version=1;
	}
	
}

sub run_checker {
	my $query = $_[0];
	print $query->start_pre;
	my $logfile = 'out/request_'.time().'_'.$$.'.kif'; # create a unique file name from timestamp and PID
	if (! open LOGFILE, "> $logfile") {
		print "ERROR: $!\nCan't create logfile \"$logfile\"!\n";
		return;
	};
	print LOGFILE '; request from '.$query->remote_user().' @ '.$query->remote_addr().' ('.$query->remote_host().')'."\n";
	print LOGFILE (';' x 80)."\n";
	print LOGFILE ';;; GDL ;;;'."\n";
	print LOGFILE (';' x 80)."\n";
	print LOGFILE $gdl."\n";

	# print "writing temporary file ...\n";
	my $tmpfile = File::Temp->new(SUFFIX => '.kif');
	print $tmpfile $gdl."\n";
	close $tmpfile;

	print "starting eclipse ...\n";
	my $timeout=10+$run_simulations_time+$run_dfs_time;
	my $check_gdl_options="[dfs_check_time:$run_dfs_time, random_check_time:$run_simulations_time, maxdepth:1000, gdl_version:$gdl_version]";
	my $command = "./run_eclipse.sh $timeout 1048576 -- -e 'set_stream_property(output, flush, end_of_line), set_stream_property(error, flush, end_of_line), ensure_loaded(\"prolog/game_checker/game_description_checker\"), open(\"".$tmpfile->filename."\",read,Stream), read_string(Stream, end_of_file, _, GDL), close(Stream), game_description_checker:check_gdl(GDL, $check_gdl_options)'";
	    
	# print "running $command\n";
	if(!open ECLIPSESTREAM, $command." 2>&1 |") {
		print "ERROR: $!\nCan't run command: $command\n";
		return;
	};
	print LOGFILE (';' x 80)."\n";
	print LOGFILE ';;; Results from check_gdl ;;;'."\n";
	print LOGFILE '; options: '.$check_gdl_options."\n";
	print LOGFILE (';' x 80)."\n";
	print $query->end_pre;
	my $line;
	my $linenum=1;
	my $anchorname;
	while($line = <ECLIPSESTREAM>) {
		chomp($line);
		$anchorname='line'.$linenum;
		print '<pre>'.$line.'</pre><a name="'.$anchorname.'"></a>';
		print '<script type="text/javascript">window.location.hash="'.$anchorname.'";</script>'."\n".("\0" x 8192);
		print LOGFILE '; '.$line."\n";
		$linenum++;
	}
	close ECLIPSESTREAM;
	print LOGFILE (';' x 80)."\n";
	close LOGFILE;
	print "<pre>done.</pre>\n";
}

sub main {
	my $q = CGI->new;
	parse_query($q); # fill up some information from the query
	print
		$q->header, # create the HTTP header
		$q->start_html('Game Checker'),
		$q->h1('Game Checker'),
		<<HTML,
		<p>Game Checker checks game descriptions written in <a href="http://en.wikipedia.org/wiki/Game_description_language">GDL</a> for compliance with the <a href="http://games.stanford.edu/language/spec/gdl_spec_2008_03.pdf">GDL specification</a>. It checks for
		<ul>
			<li>syntactic errors (missing parantheses, etc.),</li>
			<li>syntactic properties of the GDL (stratified rules, safety of variables, recursion restriction, ...), and</li>
			<li>playability, winnability and finiteness of the game</li>
		</ul>
		Playability, winnability and finiteness are only checked by brute force with either a depth first search of the game tree (enter a non-zero value for "Run depth first search for how many seconds?" below) or random simulations of the game (enter a non-zero value for "Run random simulations for how many seconds?" below). Only, if the depth first search traverses the whole game tree playability, winnability and finiteness are proven.
		</p>
		<p>Game Checker is a part of <a href="http://www.general-game-playing.de/research.html" target="_blank">Fluxplayer</a>. It runs on <a href="http://www.eclipseclp.org/" target="_blank">ECLiPSe</a> (the prolog system).</p>
		<p>Contact <a href="http://www.inf.tu-dresden.de/index.php?node_id=1373&ln=en" target="_blank">Stephan Schiffel</a> for questions, problems, praise, ...</p>
		<script type="text/javascript">
			function please_wait()
			{
				document.getElementById("results").innerHTML="";
				document.getElementById("message").innerHTML="<p>Please wait ...</p>";
				document.getElementsByName("run")[0].style.visibility="hidden";
			}
		</script>
HTML
		'<div id="results">';
	if(defined($q->param('run')) && $q->param('run') eq "Run") {
		print $q->h2('Results from previous run');
		run_checker($q);
	}
	print
		$q->end_div,
		$q->h2('Enter game'),
		$q->start_form(
			-method=>'POST',
			-action=>'gamechecker.cgi',
			-enctype=>'multipart/form-data',
			-onsubmit=>'please_wait();'),
		$q->dl(
			$q->dt('Game Description'),
			$q->dd(
				$q->textarea(
					-name=>'gdl',
					-default=>$gdl,
					-rows=>25,
					-columns=>100)
			),
			$q->dt('GDL Version?'),
			$q->dd(
				$q->popup_menu(
					-name=>'gdl_version',
					-values=>['1','2'],
					-default=>[$gdl_version],
					-labels=>{'1' => 'regular GDL (complete information)', '2' => 'GDL-II (incomplete information, nondeterminism)'})
			),
			$q->dt('Run depth first search for how many seconds (0-600)?'),
			$q->dd(
				$q->textfield(
					-name=>'run_dfs_time',
					-default=>$run_dfs_time,
					-size=>10,
					-maxlength=>5)
			),
			$q->dt('Run random simulations for how many seconds (0-600)?'),
			$q->dd(
				$q->textfield(
					-name=>'run_simulations_time',
					-default=>$run_simulations_time,
					-size=>10,
					-maxlength=>5)
			)
		),
		'<div id="message">',
		$q->end_div,
		$q->submit(-name=>'run', -value=>'Run'),
		$q->end_form,
# 		"<!--\n";
# 	foreach (keys %ENV) {
# 		print $_.' => '.$ENV{$_}."\n";
# 	}
# 	print "user: ".`id -a`."\n";
# 	print
# 		"-->\n",
		$q->end_html; # end the HTML
}

main();
