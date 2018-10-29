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
            $uniqueName = New-GUID
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



function Select-Best
{
    # Grab a list of all the folders starting with the player name
    $individuals = Get-ChildItem -Path ($playDirectory + "*")

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
            $p1 = $individuals[$i].name
            $i++
            $p2 = $individuals[$i].name
            $i++
            "Play " + $playDirectory + $p1 + " vs. " + $playDirectory + $p2
            " Player 1 WINS, deleting player 2"
            $loser = $playDirectory + $p2
            Remove-Item -Path $loser -Recurse
        }
        $individuals = Get-ChildItem -Path ($playDirectory + "*")
    }
}

Copy-Program-If-Needed
Select-Best

# Now repopulate from offspring
$bestIndividuals = Get-ChildItem -Path ($playDirectory + "*")

# for each of these generate a copy until the total number of individuals is back to full
# ensure that the baseStrategy for each is set to an appropriate offspring so they're all different
# TBD


