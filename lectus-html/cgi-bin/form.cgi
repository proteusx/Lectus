#!/usr/bin/perl -w -CSDA

use strict;
use utf8;
use v5.022;
use Unicode::Collate;
use Encode qw(encode decode);
use Storable;
use File::Slurp; #  qw(read_dir);
use CGI;
use Cwd;
use FindBin qw($Bin);

my $uc = Unicode::Collate->new();
my $cgi = CGI->new();

#------------------------------------------------------------------------------
#  Default Dictionaries location
#  See also same variable in lectus.cgi
my $dict_dir = "./dictionaries";
#------------------------------------------------------------------------------

my $header = q{
<!DOCTYPE html>
<html lang="el">
<head>
  <meta charset="UTF-8">
  <title>LECTUS</title>
  <link rel="stylesheet" href="/css/lectus.css">
</head>
<body>
  <h1>
    Lectus
  </h1>
  };
my $form = q{
  <div>
    <form class="form-lectus" name="form_lectus">
      <div class="search-box">
        <!--- <label for="lemma">Λήμμα:    </label> --->
        <input type="text" id="lemma" name="lemma" placeholder="Enter Lemma" required>
        <button onclick="AjaxPost(event);">Search</button>
        <br><br>
        <label for="regex">Regular Expression</label>
        <input  type="checkbox" name="regex" id="regex">
      </div>
};
my $results = q{
        <div id="result"></div>
};
#------------------------------------------------------------------------------
my $dir_input = qq{
  <div class="input-dir">
    <input type="text" id="dir" name="dir" class="dir" value=$dict_dir>
    <button disabled>Enter</button>
  </div>
};
#------------------------------------------------------------------------------

my  @dicts = grep {/\.dsl/} read_dir($dict_dir);
@dicts = map { (my $s = $_) =~ s/\.dsl//; $s} @dicts;

my $dic_select = q{ <div class="dictionaries">
        <select class="dic-selector" name="dicts" id="dicts" multiple size=7>
        <optgroup label="Dictionaries">
        };
foreach my $dict (@dicts){
  $dic_select .= qq{<option value="$dict" selected>$dict</option>\n};
}

my $page = $header . $form . $dir_input . $dic_select . '</optgroup></select></div>';
$page .= $cgi->end_form;
$page .= $results;
$page .= '<script src="/lectus.js"></script>';
$page .= $cgi->end_html;
say $page;
