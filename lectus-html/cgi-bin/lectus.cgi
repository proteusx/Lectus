#!/usr/bin/perl -w
#
#-CSDA  # See  perlrun
use strict;
use utf8;
use v5.022;
use Encode qw(encode decode decode_utf8);
use File::Slurp qw(read_dir);
# Load modules from current directory
use FindBin qw($RealBin);
use lib $RealBin;
use Lectus;
# Alternative
# use File::Basename;
# use Cwd qw(abs_path);
# use lib dirname(abs_path ($0));
# use lib dirname (__FILE__);               # __FILE__ = $0

# use Data::Dumper;
# use CGI qw( -debug :standard);
use CGI;
use DBI;
$| = 1;

#  Default Dictionaries location
#  See also same variable in form.cgi
my $dict_dir = "./dictionaries";
my $idx_dir  = "./idx";


#-----------------------------------------------------
#    Fetch form data
#-----------------------------------------------------
my $cgi = CGI->new();
my $lemma_param = $cgi->param('lemma');
my $dicts_param = $cgi->param('dicts');
#-----------------------------------------------------

unless ($lemma_param){
  print $cgi->header(-charset => "UTF-8");
  say "Enter something!";
  exit;
}

my $max_matches = 20;            #TODO: Use it      # No more lemmata to return
my $search = &detone(lc decode('UTF-8', $lemma_param));

my $doc = $cgi->header(-charset => "UTF-8");
$doc .=  '<link rel="stylesheet" href="/css/lectus.css">';
$doc .= $cgi->br;
my @dicts = split(/,/, $dicts_param);
foreach my $dict (@dicts){
  my $dict_file = "$dict_dir/$dict.dsl";
  die "$dict_file not found" unless -e $dict_file;
  my $dict_index = "$idx_dir/$dict.db";
  die "$dict_index not found" unless -e $dict_index;

  # Query the index database
  my @w_matched = @{ &query($dict_index, $search) };

  if (scalar @w_matched){
    $doc .= qq{<font size="+2"><b>} . uc ($dict) . qq{</b></font><br>};
    $doc .= '<hr class="separator">';
  } else {
    # $doc .= "<b>$dict:</b> -<br>";
    # $doc .= '<hr class="separator">';
    next;                                         # Stop if nothing in index
  }
  open (IN, '<', $dict_file) or die $!;
  foreach (@w_matched) {
    my ($head, $word, $idx) = @$_;
    seek IN, $idx, 0;
    my $body = "";
    while(1){
      my $line = decode('UTF-8',<IN>) ;
      last unless $line =~ /\t\[m\d?\]/;
      # $line =~ s/\s*\[\/?m\d?\]//g;
      if ( $line =~ m/\s*\[m\d?\]/ ){
        $line =~ s/\s*\[(m\d?)\]/<p class="$1">/;
        $line =~ s/\s*\[m\d?\]//g;
      }
      else
      {
        $line =~ s/\s*\[m\d?\]/<p>/;

      }
      $line =~ s!(?:\[/m\])|$!</p>!g;
      # die $line;
      $body .= $line;                                # . '<br>';
    }
    # $body =~ s/\s*\[\/?m\d?\]//g;
    &colour_html($body);
    # &decolour($body);                            # Remove colour markups.

    $doc .=   '<b><font face=Arial size="+1">' . decode_utf8($word) . '</font></b>';
    $doc .=  "$body<br>";
  } # --- End foreach keys
  $doc .=  '<br> <br>';
  close IN;
} # --- End foreach $dic
say encode('UTF-8', $doc);
# say $doc;


sub query
{
  my $dict_index = shift;
  my $search = shift;
  # warn $search;
  my $db_table = "word_index";
  my $dsn = qq(DBI:SQLite:dbname=$dict_index;,,,{ RaiseError=>1});
  my $dbh = DBI->connect($dsn) or die $DBI::errstr;

  my $sql = qq{SELECT HEAD, HEADWORD, OFFSET FROM $db_table WHERE HEAD LIKE ? };
  my $sth = $dbh->prepare($sql) or die ("Cannot Prepare:  " . $DBI::errstr);
  $sth->execute($search) or die("Cannot Execute: " . $DBI::errstr);

  my @w_matched = sort{ $a->[0] cmp $b->[0] } @{$sth->fetchall_arrayref()};
  # my $matched_ref = $sth->fetchall_arrayref();
  $dbh->disconnect();
  return \@w_matched;

}
