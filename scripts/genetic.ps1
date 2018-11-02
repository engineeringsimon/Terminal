param (
    [string]$player = "Katara",
    [int]$generation = 0,
    [int]$PopulationSize = 64,
    [int]$SelectionSize = 8
    )
    
$sourceDirectory = ".\algos\" + $player
$playDirectory = ".\genetic_" + $player + "\"
$baseFilename = "baseStrategy.pickle"
$mutatedFilename = "mutatedStrategy.pickle"
$offspringBase = "offspring" # for offspring00.pickle etc.

"Player is " + $player
"Starting generation is " + $generation
"Population size is " + $PopulationSize
"Selection size is " + $SelectionSize

function Copy-Program-If-Needed
{
    if (-not (Test-Path -Path $playDirectory))
    { 
        # copy the player if needed
        $playDirectory + " does not exist, so we need to populate it with " + $player
        for ($i = 0; $i -lt $PopulationSize; $i++)
        {
            $uniqueName = "best" + $i
            $destDirectory = $playDirectory + $uniqueName
            Copy-Item $sourceDirectory -Destination $destDirectory -Recurse
        }
    }
    else
    {
        $playDirectory + " exists, so we continue from Generation " + $generation
    }
}



<#
    Input parameters: 
    - population size (nPop)
    - number selected each iteration (nSel)
    - eval method (TBD to investigate most efficient options)
    - player
    - iteration to start at
    
    The general plan is to copy the source algorithm into nPop different copies in the playDirectory.
    
    The this script plays lots of games and selects nSel of the top algorithms, deletes the remainder.
    
    Repopulates the rest of the population from the offspring of the winners (by mutation)
    
    evaluate again.
    
    
    Evaluation ideas:
    - Tournament (most efficient)
    - bubble sort
    - shuffle, then random matches between adjacent algorithms to swap their order in a ladder competition. Run a limited number of matches.
    - random matches and maintain an ELO rating. Make sure everyone plays a minimum number of games
    - something else.
    
    Importantly, the result only needs to seperate the good nSel individuals from the rest in the face of noisy comparison.
    
#>

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

function Select-Best
{
    # Grab a list of all the folders starting with the player name
    $individuals = Get-ChildItem -Path ($playDirectory + "*") | Sort-Object {Get-Random}

    # the plan is a knockout.
    # pick two players
    # play a game
    # delete the loser
    # continue
    while ($individuals.length -ge (2 * $SelectionSize))
    {
        $i = 0
        while ($i -lt $individuals.length)
        {
            $p1 = $playDirectory + $individuals[$i].name
            $i++
            $p2 = $playDirectory + $individuals[$i].name
            $i++
            "Play " + $p1 + " vs. " + $p2
            $winnerIndex = Play-And-Return-Winner $p1 $p2
            "Winner is " + $winnerIndex
            if ($winnerIndex -eq 1)
            {
                "deleting player 2"
                $loser = $p2
            }
            else
            {
                "deleting player 1"
                $loser = $p1
            }
            Remove-Item -Path $loser -Recurse
        }
        $individuals = Get-ChildItem -Path ($playDirectory + "*") | Sort-Object {Get-Random}
    }
}

function Repopulate
{
    $bestIndividuals = Get-ChildItem -Path ($playDirectory + "*") | Sort-Object {Get-Random}
    for ($i = 0; $i -lt $bestIndividuals.length; $i++)
    {
        $newName = "Best" + $generation + "-" + $i
        Rename-Item -Path $bestIndividuals[$i] -NewName $newName
    }
    $bestIndividuals = Get-ChildItem -Path ($playDirectory + "*") | Sort-Object {Get-Random}
    
    $n = $bestIndividuals.length
    while ($n -lt $PopulationSize)
    {
        $numBest = $bestIndividuals.length
        for ($i = 0; $i -lt $numBest; $i++)
        {
            $originalIndividual = $bestIndividuals[$i]
            $uniqueName = $originalIndividual.name + "-" + $n
            $dest = $playDirectory + $uniqueName
            Copy-Item $originalIndividual -Destination $dest -Recurse
            $basePath = $dest + "\" + $baseFilename
            $offspringPath = $dest + "\" + $offspringBase + "{0, 1:d2}.pickle" -f $i
            Remove-Item -Path $basePath
            Copy-Item  $offspringPath -Destination $basePath 
            
            $n++
            if ($n -ge $PopulationSize)
            {
                break
            }
        }
    }
# for each of these generate a copy until the total number of individuals is back to full
# ensure that the baseStrategy for each is set to an appropriate offspring so they're all different
}
Copy-Program-If-Needed

for ($i = 0; $i -lt 1000000; $i++)
{
    "----------------------------------------------------------------------"
    "Starting Generation " + $generation
    Select-Best
    Repopulate
    $generation++
}

# Now repopulate from offspring




