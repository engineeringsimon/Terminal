param (
    [string]$player = "Katara",
    [int]$generation = 0,
    [int]$PopulationSize = 64,
    [int]$SelectionSize = 8,
    [string]$Role = "Master"
    )


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
    
$sourceDirectory = ".\algos\" + $player
$playDirectory = ".\pgenetic_" + $player + "\"
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
            elseif ($winner -eq 2)
            {
                "deleting player 1"
                $loser = $p1
            }
            else
            {
                break
            }
            Remove-Item -Path $loser -Recurse
        }
        $individuals = Get-ChildItem -Path ($playDirectory + "*") | Sort-Object {Get-Random}
    }
}

function Delete-Loser
{
    param ([string] $file)
    $content = Get-Content $file
    $winner = $content[0]
    $loser = $content[1]
    "Winner (" + $winner + "), Loser (" + $loser + ")"
    Remove-Item -Path $loser -Recurse
    Remove-Item $file
}

function Delete-Losers
{
    "Deleting Losers"
    $completeFiles = Get-ChildItem -File ($playDirectory + "*.complete")
    foreach ($file in $completeFiles)
    {
        Delete-Loser $file
    }
}

function Num-Remaining-Algos
{
    $remainingFiles = Get-ChildItem -Directory $playDirectory
    return $remainingFiles.Length
}

function Add-Pending-Files
{
    "Add-Pending-Files"
    $remainingFiles = Get-ChildItem -Directory $playDirectory | Sort-Object {Get-Random}
    $n = $remainingFiles.Length
    $i = 0
    while ($i -lt $n)
    {
        $p1 = $remainingFiles[$i].name
        $i++
        if ($i -ge $n)
        {
            break
        }
        
        $p2 = $remainingFiles[$i].name
        $i++
        
        $outBasename = New-Guid
        $outPath = $playDirectory + $outBasename + ".pending"
        Out-File -FilePath $outPath -InputObject $p1
        Out-File -FilePath $outPath -InputObject $p2 -Append
    }
}

<#
    Slave Behaviour
    - Find pending files, if none, wait a bit and retry.
    - Attempt renaming of a pending file to .inprogress, if fails, goto step 1
    - Read the file contents to get the algos to compete
    - play match and find the winner
    - Write result (winner and loser) to .complete file
    - delete .inprogress file
    - if slave goto step 1
#>
function Perform-Slave-Task
{
    "Slave Task"
    $isSuccessful = $false
    while (-not $isSuccessful)
    {
        $pendingFiles = Get-ChildItem -File ($playDirectory + "*.pending") | Sort-Object {Get-Random}
        $numPending = $pendingFiles.Length
        if ($numPending -eq 0)
        {
            Start-Sleep -Seconds 1
            return
        }
        $chosenFile = $pendingFiles[0]
        [string]$newName = $chosenFile.name + ".inprogress"
        [string]$chosenFilename = $chosenFile.FullName
        Rename-Item $chosenFilename -NewName $newName -ErrorVariable theError -ErrorAction SilentlyContinue
        if (-not $theError)
        {
            $isSuccessful = $true
            "Starting " + $chosenFile
        }
        else
        {
            "Yaarrgghh!!"
            $theError
        }
    }
    
    $fileContents = Get-Content ($playDirectory + $newName)
    $p1 = $playDirectory + $fileContents[0]
    $p2 = $playDirectory + $fileContents[1]
    $winnerIndex = Play-And-Return-Winner $p1 $p2
    $winner = $p1
    $loser = $p2
    if ($winnerIndex -eq 2)
    {
        $winner = $p2
        $loser = $p1
    }
    
    $outBasename = New-Guid
    $outPath = $playDirectory + $outBasename + ".complete"
    Out-File -FilePath $outPath -InputObject $winner
    Out-File -FilePath $outPath -InputObject $loser -Append
    $fileToDelete = $chosenFile.DirectoryName + "\" + $newName
    Remove-Item -Path $fileToDelete
}

function Parallel-Select-Best
{
    $numRemainingAlgos = Num-Remaining-Algos
    while ($numRemainingAlgos -ge (2 * $SelectionSize))
    {
        # determine current state so that we can easily resume
        $pendingFiles = Get-ChildItem -File ($playDirectory + "*.pending")
        $inProgressFiles = Get-ChildItem -File ($playDirectory + "*.inprogress")
        $completeFiles = Get-ChildItem -File ($playDirectory + "*.complete")
        
        $numPending = $pendingFiles.Length
        $numInProgress = $inProgressFiles.Length
        $numComplete = $completeFiles.Length
        
        <#
            Master Behaviour
            The possible actions at this point are:
            - if no more pending or in progress, and there are complete files, then delete all the losers and remove the .complete files
            - if there are no pending, inprogress, or complete files, then add .pending files if we haven't got the selection number yet
            - if there are pending or inprogress files, then be a slave and play one match
            
            Slave Behaviour
            - Find pending files, if none, wait a bit and retry.
            - Attempt renaming of a pending file to .inprogress, if fails, goto step 1
            - Read the file contents to get the algos to compete
            - play match and find the winner
            - Write result (winner and loser) to .complete file
            - delete .inprogress file
            - if slave goto step 1
            
        #>
        
        if (($numPending -eq 0) -and ($numInProgress -eq 0) -and ($numComplete -gt 0))
        {
            Delete-Losers
        }
        elseif (($numPending -eq 0) -and ($numInProgress -eq 0) -and ($numComplete -eq 0))
        {
            Add-Pending-Files
        }
        elseif ($numPending -gt 0)
        {
            Perform-Slave-Task
        }
        else
        {
            "Master awaits round completion"
            Start-Sleep -Seconds 1
        }
        $numRemainingAlgos = Num-Remaining-Algos
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
            $random_var = Get-Random -Minimum 0.0 -Maximum 1.0
            if ($random_var -lt 0.95)
            {
                Copy-Item  $offspringPath -Destination $basePath 
            }
            
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

if ($role -eq "Master")
{
    Copy-Program-If-Needed
    
    for ($i = 0; $i -lt 1000000; $i++)
    {
        "----------------------------------------------------------------------"
        "Starting Generation " + $generation
        Parallel-Select-Best
        Repopulate
        $generation++
    }
}
else
{
    for ($i = 0; $i -lt 1000000; $i++)
    {
        Perform-Slave-Task
    }
}





