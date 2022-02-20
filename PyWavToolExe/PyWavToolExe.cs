using System.Diagnostics;

internal class PyWavToolExe
{
    static void Main(string[] args)
    {
        String python = ".\\python-3.9.10\\python.exe";
        String endpoint = ".\\src\\PyWavTool.py";
        Process p = Process.Start(python, endpoint + " " + String.Join(" ", args));
        p.WaitForExit();
    }
}