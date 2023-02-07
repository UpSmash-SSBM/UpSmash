const createWindowsInstaller = require('electron-winstaller').createWindowsInstaller
const path = require('path')

getInstallerConfig()
  .then(createWindowsInstaller)
  .catch((error) => {
    console.error(error.message || error)
    process.exit(1)
  })

function getInstallerConfig () {
  console.log('creating windows installer')
  const rootPath = path.resolve()
  console.log(rootPath)
  const outPath = path.join(rootPath, 'release-builds')
  console.log(outPath)

  return Promise.resolve({
    appDirectory: path.join(outPath, 'UpSmash-win32-ia32/'),
    authors: 'Ryan Yeung',
    noMsi: true,
    outputDirectory: path.join(outPath, 'windows-installer'),
    exe: 'UpSmash.exe',
    setupExe: 'UpSmashInstaller.exe',
    setupIcon: path.join(rootPath, 'assets', 'icons', 'win', 'icon.ico')
  })
}