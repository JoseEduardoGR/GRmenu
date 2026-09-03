# frozen_string_literal: true

Gem::Specification.new do |spec|
  spec.name          = "grmenu"
  spec.version       = "4.0.3"
  spec.authors       = ["grcode"]
  spec.email         = ["garabatoangelopolis@gmail.com"]

  spec.summary       = "Menu de navegacion interactivo para terminal con Banners ASCII 3D, colores y estilos"
  spec.description   = "GRmenu es una gema ligera para crear menus interactivos de navegacion en terminal (Linux/macOS/Windows) usando flechas arriba/abajo y Enter, con soporte para Banners ASCII 3D, paleta de colores y estilos de marco, sin dependencias externas."
  spec.homepage      = "https://github.com/JoseEduardoGR/GRmenu"
  spec.license       = "MIT"
  spec.required_ruby_version = ">= 2.6.0"

  spec.metadata["source_code_uri"] = "https://github.com/JoseEduardoGR/GRmenu"
  spec.metadata["bug_tracker_uri"] = "https://github.com/JoseEduardoGR/GRmenu/issues"
  spec.metadata["changelog_uri"]   = "https://github.com/JoseEduardoGR/GRmenu/commits/main"

  spec.files = [
    "grmenu.rb",
    "README.md",
    "LICENSE",
    "data/borders.json",
    "data/colors.json",
    "data/fonts.json",
    "data/help.txt",
    "data/themes/cyberpunk.gr",
    "data/themes/dracula.gr",
    "data/themes/matrix.gr",
    "data/themes/monokai.gr",
    "data/themes/neon_red.gr",
    "data/themes/nord.gr",
    "data/themes/sunset.gr"
  ]
  spec.extra_rdoc_files = ["README.md"]
  spec.rdoc_options     = ["--main", "README.md"]
  spec.require_paths    = ["."]
end
