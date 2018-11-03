"dodgy rename"
Rename-Item aaafasf.txtrst -NewName sfgsfgsdfg -ErrorVariable theError1 -ErrorAction SilentlyContinue
$theError1
if ($theError1)
{
    "The error is true"
}
else
{
    "the error is false"
}

"good 1"
Rename-Item latestMatch.txt -NewName latestMatch.txt1 -ErrorVariable theError2 -ErrorAction SilentlyContinue

$theError2
if ($theError2)
{
    "The error is true"
}
else
{
    "the error is false"
}
"and back"
Rename-Item latestMatch.txt1 -NewName latestMatch.txt -ErrorVariable theError3 -ErrorAction SilentlyContinue

$theError3
if ($theError3)
{
    "The error is true"
}
else
{
    "the error is false"
}