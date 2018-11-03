Get-Job | Remove-Job


Start-Job -Name M1 -ScriptBlock {
    Get-Location
    java -jar D:\Documents\git\Terminal\engine.jar work D:\Documents\git\Terminal\algos\Moon\run.ps1 D:\Documents\git\Terminal\algos\Bumi\run.ps1 
}

Start-Job -Name M2 -ScriptBlock {
    Get-Location
    java -jar D:\Documents\git\Terminal\engine.jar work D:\Documents\git\Terminal\algos\SkyBison\run.ps1 D:\Documents\git\Terminal\algos\Katara\run.ps1 
}

Get-Job | Wait-Job | Receive-Job