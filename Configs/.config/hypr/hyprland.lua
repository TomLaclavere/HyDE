-- Hyprland loads this file when it is started without a config, and it prefers
-- it over hyprland.conf. HyDE loads it too, last, as the override layer below.
-- The block keeps the two apart: hyde.lua sets `hyde` on its first line, so it
-- runs only when this file is the entry point and HyDE has not been loaded.
-- Removing it leaves a session with a cursor and nothing else.
if not hyde then
	local share = os.getenv("XDG_DATA_HOME") or (os.getenv("HOME") .. "/.local/share")
	local entry = share .. "/hypr/hyde.lua"
	local handle = io.open(entry, "r")
	if not handle then
		error("HyDE is not installed at " .. entry .. ". Run install.sh -r, or point Hyprland at your own config.")
	end
	handle:close()
	dofile(entry)
end

-- Your Hyprland configuration. HyDE never overwrites this file.
--
-- It loads after HyDE's own binds, so settings here take precedence. Replacing
-- a bind needs more than that: see below. HyDE's defaults live in
-- ~/.local/share/hypr/lua/ and are overwritten on every update, so edits there
-- do not survive.
--
-- Adding a keybind:
--
--     hl.bind("SUPER + SPACE", hl.dsp.exec_cmd(hyde.sh.gamelauncher()), {
--         description = "[Utilities] game launcher",
--     })
--
-- Replacing one of HyDE's: bind the same combination again and yours takes
-- over, but copy its flags across as well. A bind counts as the same one only
-- when its flags match, and `description` is not a flag — miss one and both
-- binds stay live on that combination. Copy the whole options table from
-- ~/.local/share/hypr/lua/key_binds.lua and change only what you need:
--
--     hl.bind("F9", hl.dsp.exec_cmd(hyde.sh.volumecontrol("-o", "m")), {
--         locked = true,
--         description = "[Hardware Controls|Audio] un/mute output",
--     })
--
-- Press SUPER + / to see what is actually loaded, your own binds included.
-- The full reference is KEYBINDINGS.md in the HyDE repository.
--
-- Other Lua files next to this one can be pulled in with require("name").

-- ── Perso (TomLaclavere) ────────────────────────────────────────────────────
-- Les moniteurs sont dans monitors.lua (généré par nwg-displays), que HyDE
-- charge tout seul.

hl.config({
    input = {
        kb_layout = "fr",
        resolve_binds_by_sym = true,
        numlock_by_default = true,
        touchpad = { natural_scroll = true },
    },
    decoration = { rounding = 23 },
    general = { gaps_in = 3, gaps_out = 5, border_size = 2 },
})

-- Thème GTK / icônes / curseur Dracula (réappliqué à chaque reload)
for _, cmd in ipairs({
    "gsettings set org.gnome.desktop.interface icon-theme 'Tela-circle-dracula'",
    "gsettings set org.gnome.desktop.interface gtk-theme 'Dracula'",
    "gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'",
    "gsettings set org.gnome.desktop.interface cursor-theme 'Dracula-cursors'",
    "gsettings set org.gnome.desktop.interface cursor-size 25",
    "hyprctl setcursor Dracula-cursors 25",
}) do
    hl.exec_cmd(cmd)
end

hl.on("hyprland.start", function()
    hl.exec_cmd("xsettingsd")
end)

-- Raccourcis perso
hl.bind("SUPER + SHIFT + L", hl.dsp.exec_cmd("toggle-laser-cursor.sh"), {
    description = "[Utilities] toggle laser pointer cursor",
})
-- Super + / est peu pratique en AZERTY : aide des raccourcis aussi sur Super + ;
hl.bind("SUPER + semicolon", hl.dsp.exec_cmd(hyde.sh.menu.binds()), {
    description = "[Launcher|Rofi menus] keybindings hint",
})
-- Apps par défaut : thunar, brave, code (remplace les binds HyDE, sans flags)
hl.bind("SUPER + E", hl.dsp.exec_cmd("thunar"), { description = "[Launcher|Apps] file explorer" })
hl.bind("SUPER + B", hl.dsp.exec_cmd("brave"), { description = "[Launcher|Apps] browser" })
hl.bind("SUPER + C", hl.dsp.exec_cmd("code"), { description = "[Launcher|Apps] text editor" })
