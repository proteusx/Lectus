package Lectus;

require Exporter;
@ISA = qw(Exporter);
@EXPORT = qw(dict_indexer detone colour_Ansi colour_html);
use strict;
use utf8;
use v5.022;
use Encode qw( decode_utf8 );                 # Needed for SQLite greek text
# use open qw(:std :encoding(UTF-8));         # Hangs cgi script for Greek input
use Unicode::Normalize;
use File::Slurp;                              # qw(read_dir);
use experimental 'smartmatch';                # silence smartmatch (~~) warning;

sub dict_indexer
{
  use Parallel::ForkManager;
  my $idx_dir = "./idx/";
  my $db_table = "word_index";
  my $pm = Parallel::ForkManager->new(7);
  my $dict_dir = shift @_;
  print "Indexing $dict_dir\*\.dsl  ...\n";
  my @dicts = grep {/\.dsl/} read_dir("$dict_dir");
  @dicts = map { (my $s = $_) =~ s/\.dsl//; $s} @dicts;
  # $| = 1;
  foreach my $dict (@dicts){
    my $pid = $pm->start and next;
    my $dict_file = $dict_dir . $dict . '.dsl';
    my $dict_index = $idx_dir . $dict . '.db';
    unlink $dict_index if -e $dict_index;

    print "$dict ...";
    my @stopwords = qw/and α και μεν δε δ ο η γ το του σου σε σ της των αι οι τα εν ω/;
    my $dsn = qq(DBI:SQLite:dbname=$dict_index;,,,{ RaiseError=>1, AutoCommit=>1});
    my $dbh = DBI->connect($dsn) or die $DBI::errstr;
    $dbh->do("PRAGMA synchronous = OFF");             # otherwise insertions are too slow
    my $tbl = qq{ CREATE TABLE IF NOT EXISTS $db_table
                      (ID INTEGER PRIMARY KEY NOT NULL,
                        HEAD TEXT,
                        HEADWORD TEXT,
                        OFFSET  INTEGER NOT NULL);
                };
    my $rv = $dbh->do($tbl);
    die ("Table creation error" . $DBI::errstr) if $rv < 0;
    #
    # Prepare insertion command
    #
    my $sql = qq{INSERT INTO $db_table (HEAD, HEADWORD, OFFSET) VALUES(?, ?, ?);};
    my $sth = $dbh->prepare($sql) or die("cannot prepare: " . $DBI::errstr);

    my @entries;
    my $offset = 0;
    my $head;
    my $d_head;
    my $body_lines = 1;
    my @prev_d_heads;                  # Store detoned heads for bodyless lemmata
    open (IN, '< :encoding(UTF-8)', $dict_file) or die $!;
    while (<IN>) {
      next if /#/;
      next if /^\s*$/;
      unless (/^\t/){                  # Line is a headword
        push @prev_d_heads, [$d_head, $head];
        $offset = tell(IN);
        my $head = $_;
        $head =~ s/(\n|\r)//g;           # Need this for DOS \n\r. Chomp leaves \r
        $head =~ s/\x{feff}//;
        my @heads = split /\s+/, $head;
        foreach (@heads){
          $d_head = &detone($_);
          $d_head =~ s/(\,|\.|\'|᾽)$//;
          next if $d_head ~~ @stopwords;       # Do not enter stop words
          push @entries, [$d_head, $offset, $head];
        }
        #-------------------------------------------------------------
        #      Offsets of bodyless lemmata are set to the first
        #      lemma that has a body.  Good for Beeks but may give
        #      silly results in other dictionaries
        #-------------------------------------------------------------
        if ($body_lines eq 0){
          push @entries, [$_->[0], $offset, $_->[1]] foreach @prev_d_heads;
        }
        $body_lines = 0;                  # Reset lines counter
      } else {                            # Line is explanation text
        $body_lines++;                    # We have text lines
        @prev_d_heads =();                # Reset empty heads counter
      }  # -- End unless /^t/
    }    # -- End while <IN>
    close IN;
    @entries = sort {$a->[0] cmp $b->[0]} @entries;
    my (@d_heads, @offsets, @heads);
    foreach my $entry (@entries){
      push @d_heads, $entry->[0];
      push @offsets, $entry->[1];
      push @heads,   $entry->[2];
    }
    $sth->execute_array({}, \@d_heads, \@heads, \@offsets);
    $sth->finish;
    $dbh->disconnect();
    print " ok.\n";
    $pm->finish;
  }  # end foreach @dict
  $pm->wait_all_children;
  say "All done.";
  return;
}

sub detone
{
  my $head = shift @_;
  # $head =~ s/\{+\*\}+//g;
  $head =~ s/[\}\{\(\)\*\]\[\\]+//g;
  $head =~ s/[0-9]+?\.?//g;
  $head = NFD($head);
  $head =~ s/\pM*//g;
  $head = lc $head;
  $head =~ s/\s+/ /;
  return $head;
}

sub colour_Ansi
{
  my $reset='[0m';
  my $red='[0;31m';
  my $green='[0;32m';
  my $yellow='[0;33m';
  my $blue='[0;34m';
  my $purple='[0;35m';
  my $cyan='[0;36m';

  $_[0] =~ s/\[\/?i\]//g;                        # Italics out
  $_[0] =~ s/\[c\s+(?:\w+?)?green\]/$green/g;
  $_[0] =~ s/\[c\s+(?:\w+?)?blue\]/$blue/g;
  $_[0] =~ s/\[c\s+(?:\w+?)?magenta\]/$purple/g;
  $_[0] =~ s/\[c\s+(?:\w+?)?purple\]/$purple/g;
  $_[0] =~ s/\[c\s+(?:\w+?)?red\]/$red/g;
  $_[0] =~ s/\[c maroon\]/$red/g;
  # $_[0] =~ s/(\[c gray\])|(\[p\])/$cyan/g;
  $_[0] =~ s/(\[c\s+(?:\w+?)?gray\])|(\[p\])/$cyan/g;
  $_[0] =~ s/\[c\s+(?:\w+?)?yellow\]/$yellow/g;
  $_[0] =~ s/\[b\]/$yellow/g;
  $_[0] =~ s/\[ref]/$cyan/g;
  $_[0] =~ s/\[\/[bcp]\]/$reset/g;
  $_[0] =~ s/\[\/ref]/$reset/g;
  $_[0] =~ s/\\</</g;
  $_[0] =~ s/\\>/>/g;
  $_[0] =~ s/\\~/~/g;
  $_[0] =~ s!\[/?ex]!!g;
  $_[0] =~ s!\[/?trn]!!g;
  $_[0] =~ s!\[/?lang(?: id=\d+)?]!!g;
  $_[0] =~ s!\[/?c(?: [a-z]+)?\]!!g;
  $_[0] =~ s/\\\[/{/g;                          # \[ -> [
  $_[0] =~ s/\\\]/}/g;                          # \] -> ]
}

#-----------------------------------------------------------

sub decolour
{
  $_[0] =~ s/\[\/?c.*?\]//g;
  $_[0] =~ s/\[\/?b\]//g;

}

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

1;
