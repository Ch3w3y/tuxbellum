# Install desktop entry
install_data(
  'tuxbellum.desktop',
  install_dir: get_option('datadir') / 'applications',
)

# Install metainfo
install_data(
  'tuxbellum.metainfo.xml',
  install_dir: get_option('datadir') / 'metainfo',
)

# Install icons
install_subdir(
  'icons',
  install_dir: get_option('datadir') / 'icons' / 'hicolor',
  strip_directory: false,
)
