use scripting additions

property missingWindowChecks : 0

on editorCommand(argumentsText)
	set appPath to POSIX path of (path to me)
	return (do shell script (quoted form of (appPath & "/Contents/Resources/Scripts/activate.sh") & argumentsText))
end editorCommand

on run
	set missingWindowChecks to 0
	editorCommand("")
end run

on reopen
	set missingWindowChecks to 0
	editorCommand("")
end reopen

on idle
	try
		editorCommand(" --status")
		set missingWindowChecks to 0
	on error
		set missingWindowChecks to missingWindowChecks + 1
		if missingWindowChecks ≥ 2 then quit
	end try
	return 2
end idle

on quit
	try
		editorCommand(" --quit")
	end try
	continue quit
end quit
