
# run_all_trials.ps1
# Runs all Maze Tycoon batch variations (algs x gens, plus heuristics for A* variants)
# Usage from repo root:
#   powershell -ExecutionPolicy Bypass -File .\run_all_trials.ps1
# Optional args:
#   -ResultsDir "C:\path\to\results"
#   -Width 31 -Height 31 -Trials 50

param(
    [string]$ResultsDir = ".\results",
    [int]$Width = 31,
    [int]$Height = 31,
    [int]$Trials = 50,
    [string]$Mode = "batch"
)

$ErrorActionPreference = "Stop"

# Ensure output dir exists
New-Item -ItemType Directory -Force -Path $ResultsDir | Out-Null

$gens = @("dfs_backtracker", "prim")
$algs_basic = @("bfs", "dijkstra")
$algs_heur = @("a_star", "bidirectional_a_star")
$heurs = @("manhattan", "euclidean", "octile")

Write-Host "=== Maze Tycoon Batch Runner ==="
Write-Host "ResultsDir: $ResultsDir"
Write-Host "Size: ${Width}x${Height} | Trials: $Trials"
Write-Host "Generators: $($gens -join ', ')"
Write-Host "Algorithms: $($algs_basic + $algs_heur -join ', ')"
Write-Host "Heuristics (A* variants): $($heurs -join ', ')"
Write-Host "--------------------------------"

function Run-Variant {
    param(
        [string]$Alg,
        [string]$Gen,
        [string]$Heuristic = $null
    )

    if ($Heuristic) {
        $outfile = Join-Path $ResultsDir ("results_{0}_{1}_{2}_{3}x{4}_t{5}.jsonl" -f $Alg, $Heuristic, $Gen, $Width, $Height, $Trials)
        $cmd = @(
            "python", "-m", "maze_tycoon.game.app",
            "--mode", $Mode,
            "--alg", $Alg,
            "--heuristic", $Heuristic,
            "--gen", $Gen,
            "--width", $Width,
            "--height", $Height,
            "--trials", $Trials,
            "--jsonl", $outfile
        )
    } else {
        $outfile = Join-Path $ResultsDir ("results_{0}_{1}_{2}x{3}_t{4}.jsonl" -f $Alg, $Gen, $Width, $Height, $Trials)
        $cmd = @(
            "python", "-m", "maze_tycoon.game.app",
            "--mode", $Mode,
            "--alg", $Alg,
            "--gen", $Gen,
            "--width", $Width,
            "--height", $Height,
            "--trials", $Trials,
            "--jsonl", $outfile
        )
    }

    Write-Host ""
    Write-Host ("Running: {0} | Gen: {1}{2}" -f $Alg, $Gen, $(if ($Heuristic) { " | Heur: $Heuristic" } else { "" }))
    Write-Host ("Output -> {0}" -f $outfile)

    & $cmd[0] $cmd[1..($cmd.Length-1)]
}

# Basic algorithms (no heuristic)
foreach ($gen in $gens) {
    foreach ($alg in $algs_basic) {
        Run-Variant -Alg $alg -Gen $gen
    }
}

# Heuristic algorithms (A* variants)
foreach ($gen in $gens) {
    foreach ($alg in $algs_heur) {
        foreach ($h in $heurs) {
            Run-Variant -Alg $alg -Gen $gen -Heuristic $h
        }
    }
}

Write-Host ""
Write-Host "=== Done. All results in $ResultsDir ==="
