# Changelog

## [1.3.2] - 2026-04-27
### Changed
- New build orders for all strategies
- New logic for train_army that is more fexible with the available food
- New constants for improved gameplay

### Fixed
- Fix a bug where turn number didn't reset on new game
- Fix a bug where Dumb strategy couldn't sort a choice
- Fix a bug where the AI couldn't make a failed attack

## [1.3.1] - 2026-04-24
### Changed
- New logic for interface: Now menus and action dispatcher have their own classes unpacked from the View
- Information about buildings has been moved for info
- Status now show complete information about the kingdom
- Minor text changes for better readibility of the game

### Fixed
- The enemy failed actions now are shown

## [1.3.0] - "Science and Fiction" - 2026-04-23
### Added
- Gold as a new resource
- Gold producer building: Mercado
- Science research system for unlocking technologies
- Science buildings: Casa de construção, moinho and arsenal
- Info menu for detailed game information

### Changed
- New logic for the game bots: Bot class and build order strategies

## [1.2.0] - "Houses and barracks" - 2026-04-15
### Added
- Wood as a new resource
- New building options: Houses, barracks, walls and salmills
- New AI logic with tatical system
- City slots concept introduced
- Limited army training introduced

### Fixed
- Display now gives better information

## [1.1.1] - 2026-04-15
### Fixed
- Keyboard display issues

### Changed
- Refactored codebase to improve scalability

## [1.1.0] - "Mountains and beaches" - 2026-04-14
### Added
- Civilization options system
- Multiple civilization choices for players: Teresópolis, Petrópolis, Volta Redonda and Rio de Janeiro
- Players can select their civilization and the AI civilization as the game begins

## [1.0.0] - "Hello, world" - 2024-04-14
### Added
- Main game mechanics: Build economy, make armies, attack and defense
- Core gameplay features
- Three options per turn: build a farm, make an army, attack
- Open field attack and invasion attack mechanics
- Five sample AI personality options
