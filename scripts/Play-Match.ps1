function Play-And-Return-Winner 
{
    $p1 = $args[0]
    $p2 = $args[1]
    $algo1 = $p1 + "\run.ps1"
    $algo2 = $p2 + "\run.ps1"
    $outputContent = java -jar engine.jar work $algo1 $algo2
    
    foreach ($line in $outputContent)
    {
        if ($line.Contains("PLAYER 1 WINS"))
        {
            return 1
        }
        
        if ($line.Contains("PLAYER 2 WINS"))
        {
            return 2
        }
    }
    
    return 0
}

$p1 = $args[0]
$p2 = $args[1]

"Play " + $p1 + " vs. " + $p2
$winnerIndex = Play-And-Return-Winner $p1 $p2
"Winner is " + $winnerIndex
if ($winnerIndex -eq 1)
{
    "deleting player 2"
    $loser = $p2
}
elseif ($winnerIndex -eq 2)
{
    "deleting player 1"
    $loser = $p1
}
else
{
    return
}

Remove-Item -Path $loser -Recurse
