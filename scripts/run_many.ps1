$player = "Bumi"
$opponents = @("starter-algo", "BadgerMole", "Dragon", "SkyBison", "Moon", "Boulder", "JongJong", "Gyatso", "Paku")
# $opponents = @("Dragon", "SkyBison", "Moon", "JongJong", "Gyatso")
$wins = @()
$numMatches = 3

foreach ($opponent in $opponents)
{
    $numWins = 0
    for($i = 0; $i -lt $numMatches; $i++)
    {
        $outputFilename = $player + "_" + $opponent + "_" + $i + ".txt"
        $algo1 = ".\algos\" + $player + "\run.ps1"
        $algo2 = ".\algos\" + $opponent + "\run.ps1"
        #$out = ".\scripts\run_match.ps1 .\algos\$player .\algos\$opponent > " + $player + "_" + $opponent + "_" + $i + ".txt"
        # "Output filename = " + $outputFilename
        # $algo1
        # $algo2
        
        java -jar engine.jar work $algo1 $algo2 > $outputFilename
        
        $fileContent = Get-Content -Path $outputFilename
        foreach ($line in $fileContent)
        {
            if ($line.Contains("PLAYER 1 WINS"))
            {
                $player + " defeats " + $opponent
                $numWins += 1
                break
            }
            
            if ($line.Contains("PLAYER 2 WINS"))
            {
                $opponent + " defeats " + $player
            }
        }
    }  
    $wins += $numWins
}

for ($i = 0; $i -lt $opponents.Length; $i++)
{
    $player + " vs. " + $opponents[$i] + " => " + $wins[$i] + " / " + $numMatches
}

