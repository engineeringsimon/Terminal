param (
    [string]$player = "Iroh",
    [int]$iteration = 0
    )
    
$sourceDirectory = ".\algos\" + $player
$playerDirectory1 = ".\evolve\p1" + $player 
$playerDirectory2 = ".\evolve\p2" + $player
$baseFilename = "baseStrategy.pickle"
$mutatedFilename = "mutatedStrategy.pickle"

$base2 = $playerDirectory2 + "\" + $baseFilename
$base1 = $playerDirectory1 + "\" + $baseFilename
$mutated2 = $playerDirectory2 + "\" + $mutatedFilename
$mutated1 = $playerDirectory1 + "\" + $mutatedFilename

$temperature = 0.02
$tempChangePercent_per_turn = 0.1
$tempChangeRatio = 1.0 - ($tempChangePercent_per_turn / 100)

function Play-And-Return-Winner
{
    $outputFilename = "latestMatch" + $player + ".txt"
    $algo1 = $playerDirectory1 + "\run.ps1"
    $algo2 = $playerDirectory2 + "\run.ps1"
    java -jar engine.jar work $algo1 $algo2 > $outputFilename
    #| Tee-Object -file $outputFilename
    
    $fileContent = Get-Content -Path $outputFilename
    foreach ($line in $fileContent)
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

function Change-To-New-Program
{
    Copy-Item $base2 -Destination $base1
    "New program " + $base2 + " => " + $base1
    Copy-Item $mutated2 -Destination $base2
    "New mutation " + $mutated2 + " => " + $base2
}

function Stay-On-Same-Program
{
    Copy-Item $mutated1 -Destination $base2
    "Mutate " + $mutated1 + " => " + $base2
}

function Copy-Program-If-Needed
{
    if (-not (Test-Path -Path $playerDirectory1))
    { 
        # copy the player if needed
        Copy-Item $sourceDirectory -Destination $playerDirectory1 -Recurse 
        Copy-Item $sourceDirectory -Destination $playerDirectory2 -Recurse 
    }

}

function Play-A-Round
{
    $winner = Play-And-Return-Winner
    
    "."
    "Winner is player " + $winner

    if ($winner -eq 2)
    {
        Change-To-New-Program
    }
    elseif ($winner -eq 1)
    {
        # generate random number
        $random_var = Get-Random -Minimum 0.0 -Maximum 1.0
        if ($random_var -lt $temperature)
        {
            Change-To-New-Program
        }
        else
        {
            Stay-On-Same-Program
        }
    }
    else
    {
        "Error!"
    }
}



# Copy Iroh and rename twice to play against each other.

# play against each other

# if player 2 wins, 
#   then player 1 baseStrategy becomes player 2 baseStrategy
#   and player 2 baseStrategy becomes player 2 mutatedStrategy
# if player 1 wins,
#   then there is a probability of T (temperature k -> 0.0) of the same behaviour as if p1 wins
#   otherwise: player 2 baseStrategy becomes player 1 mutatedStrategy

Copy-Program-If-Needed

while ($iteration -lt 1000000)
{
    "Playing round " + $iteration + " with temperature " + $temperature
    $time = Measure-Command { Play-A-Round }
    $roundsPerHour = [math]::Floor(3600.0 / $time.TotalSeconds)
    "Round " + $iteration + " took " + $time.TotalSeconds + "s, which is " + $roundsPerHour + " rounds per hour."
    
    if ($iteration % 100 -eq 0)
    {
        $destFilename = $playerDirectory1 + "\baseStrategy{0, 5:d5}.pickle" -f $iteration
        Copy-Item $base1 -Destination $destFilename
        
        $backToBaseFilename = $sourceDirectory + "\" + "baseStrategy{0, 5:d5}.pickle" -f $iteration
        Copy-Item $base1 -Destination $backToBaseFilename
    }
    
    $temperature *= $tempChangeRatio
    
    $iteration += 1
}


