"Trying to work out how to do parallel tasks"

workflow helloworld 
{
    param([string[]]$stringList)
    
    foreach -parallel ($s in $stringList)
    {
        Start-Sleep -seconds 3
        $s
    }
}




Get-Job | Remove-Job
# helloworld -stringList "a", "b", "c"

for ($i = 0; $i -lt 5; $i++)
{
    $jobName = "Dude" + $i
    Start-Job -Name $jobName -ScriptBlock {
        param($numSeconds)
        Start-Sleep -seconds $numSeconds
        $numSeconds
    } -Arg $i
}

"waiting"
Get-Job | Wait-Job
"finished waiting"

Get-Job | Receive-Job

# Get-Job | Remove-Job
