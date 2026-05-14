project('tuxbellum', version: '4.0.4', meson_version: '>=1.2.0', license: 'Apache-2.0')

python = import('python').find_installation('python3')

# Install source
install_subdir('src/tuxbellum', install_dir: python.get_install_dir())

# Install packages directory to data dir
install_subdir('packages', install_dir: get_option('datadir') / 'tuxbellum')

# Install locales
install_subdir('locales', install_dir: get_option('datadir') / 'tuxbellum')

# Install data files (desktop entry, metainfo, icons)
subdir('data')

# Install license
install_data(
    'LICENSE',
    install_dir: get_option('datadir') / 'licenses' / meson.project_name(),
)
