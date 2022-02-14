#!/usr/bin/perl -w
#
#-CSDA  # See  perlrun
use strict;
use utf8;
use v5.022;
use Unicode::Collate;
use Encode qw(encode decode);
use Storable;
use File::Slurp qw(read_dir);
use CGI qw( -debug );
# use open qw( :std :encoding(UTF-8) );
binmode(STDOUT, "encoding(UTF-8)");
my $uc = Unicode::Collate->new();
$| = 1;

#  Default Dictionaries location
#  See also same variable in form.cgi
my $dict_dir = "./dictionaries";


my $cgi = CGI->new();
my $dir = $cgi->param('dir');
$dict_dir = $dir if $dir;
my $lemma_param = $cgi->param('lemma');
unless ($lemma_param){
  print $cgi->header(-charset => "UTF-8");
  say "Enter something!";
  exit;
}
# die $dict_dir;
my $search_regex = &detone(lc decode('UTF-8', $lemma_param));
my $regex_flag = 0;
$regex_flag = $cgi->param('regex');
my $idx_dir  = "./idx";
my @dicts = split(/,/, $cgi->param('dicts'));

my $max_matches = 20;                          # Maximum lemata to return
my $lemma;
unless ($regex_flag =~m/true/i){
  $lemma = qr/^$search_regex-?\d?$/;
}else{
  $lemma = qr/$search_regex/;
}
print $cgi->header(-charset => "UTF-8");
my $doc;
$doc .=  '<link rel="stylesheet" href="/css/lectus.css">';
foreach my $dict (@dicts){
  my $dict_file = "$dict_dir/$dict.dsl";
  my $dict_index = "$idx_dir/$dict.idx";
  my %w_index;

  &dict_indexer($dict) unless -e $dict_index;      # Generate index if not there

  %w_index = %{retrieve($dict_index)};


  my %w_matches = map { $_ => $w_index{$_} }  grep {/$lemma/i} keys %w_index;
  if (scalar keys %w_matches){
    $doc .= '<font size="+2"><b>'. uc $dict. "</b></font><br>";
    $doc .= '<hr class="separator">'
  } else {
    $doc .= "<b>$dict:</b> -<br>";
    $doc .= '<hr class="separator">';
    next;                                         # Stop if nothing in index
  }

  open (IN, '<', $dict_file) or die $!;
  foreach ( $uc->sort(keys %w_matches) ){
    my ($idx, $word) = @{$w_matches{$_}};            # [index, word]
    # print $word;
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
      $body .= $line; # . '<br>';
    }
    # $body =~ s/\s*\[\/?m\d?\]//g;
    &colour_html($body);
    # &decolour($body);                            # Remove colour markups.

    $doc .=   '<b><font face=Arial size="+1">' . $word . '</font></b><br>';
    $doc .=  "$body<br>";
  } # --- End foreach keys
  $doc .=  '<br> <br>';
  close IN;
} # --- End foreach $dic
say $doc;

#-----------------------------------------------------------
#               Subroutines
#-----------------------------------------------------------

sub colour_html
{
  # $_[0] =~ s/\[c\s(\w+?)\]/<span style="color: $1;">/g;
  $_[0] =~ s/\[c yellow\]/[c maroon]/g;
  $_[0] =~ s/\[c\s(\w+?)\]/<font style="color: $1;">/g;
  $_[0] =~ s!\[/c\]!</font>!g;
  $_[0] =~ s!\[/c]!</span>!g;
  $_[0] =~ s/\[b\]/<b>/g;
  $_[0] =~ s!\[/b\]!</b>!g;
  $_[0] =~ s/\[i\]/<i>/g;                        # Italics out
  $_[0] =~ s!\[/i\]!</i>!g;
  # clean redundant markups
  $_[0] =~ s!\[/?ex]!!g;
  $_[0] =~ s!\[/?trn]!!g;
  $_[0] =~ s!\[/?lang(?: id=\d+)?]!!g;
  $_[0] =~ s!\[/?p]!!g;
  $_[0] =~ s!\\\[tense\\]!!g;
  $_[0] =~ s!\\\[voice\\]!!g;
  $_[0] =~ s!\\\[dialect\\]!!g;
  $_[0] =~ s!\\~!~!g;
  #-----------------------------
  $_[0] =~ s!\\\[![!g;
  $_[0] =~ s!\\\]!]!g;
}

sub decolour
{
  $_[0] =~ s/\[\/?c.*?\]//g;
  $_[0] =~ s/\[\/?b\]//g;

}

#-----------------------------------------------------------

sub dict_indexer
{
  my $dict = shift @_;
  my $dict_idx = "$idx_dir/$dict" . '.idx';

  my %w_index;
  my %dups;
  my $offset = 0;
  my $head;
  my $d_head;
  my $body_lines = 1;
  my @prev_d_heads= ();       # Store detoned heads for bodyless lemmata
  open (IN, "<:encoding(UTF-8)", "$dict_dir/$dict" . '.dsl') or die $!;
  while (<IN>) {
    next if /#/;
    next if /^\s*$/;
    unless (/^\t/){
      push @prev_d_heads, $d_head;
      $offset = tell(IN);
      $head = $_;
      $head =~ s/(\n|\r)//g;    # Need this for DOS \n\r. chomp leaves \r
      $head =~ s/\x{feff}//;
      $d_head = &detone($head);
      unless (exists $w_index{$d_head}){
        $w_index{$d_head} = [$offset, $head];
      }else{
        if (exists($dups{$d_head})){
          $dups{$d_head}++;
          $w_index{$d_head . "-" ."$dups{$d_head}"} = [$offset, $head];
        }else{
          $dups{$d_head} = 1;
          $w_index{$d_head . "-1"} = [$offset, $head];
        }
      }  # -- End unless exists

      #-------------------------------------------------------------
      #      Offsets of bodyless lemmata are set to the first
      #      lemma that has a body.  Good for Beeks but may give
      #      silly results in other dictionaries
      #-------------------------------------------------------------
      if ($body_lines eq 0){
        @{$w_index{$_}}[0] = $offset foreach (@prev_d_heads);
      }
      $body_lines = 0;                  # Reset lines counter
    } else {
      $body_lines++;
      @prev_d_heads =();                # Reset

    }  # -- End unless /^t/
  }
  store \%w_index, $dict_idx;
  close IN;
  print " (Indexed -> $dict_idx)<br>";
  return;
}

#-----------------------------------------------------------

use Unicode::Normalize;
sub detone
{
  my $head = shift @_;
  # $head =~ s/\{+\*\}+//g;
  $head =~ s/[\}\{\(\)\*]+//;
  $head =~ s/[0-9]+//;
  $head = NFD($head);
  $head =~ s/\pM*//g;
  $head = lc $head;
  $head =~ s/\s+//;
  return $head;
}

