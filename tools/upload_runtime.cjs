// Upload verified image recipes to an unpublished preview; never replace a
// published version. Invoked only on the maintainer's Windows UX branch.
module.exports = async ({github, context, core}) => {
  const fs = require('node:fs');
  const path = require('node:path');
  const crypto = require('node:crypto');
  const {owner, repo} = context.repo;
  if (owner !== 'engeeeee' || repo !== 'egress-workbench-app' || context.ref !== 'refs/heads/windows-ux') return;
  const tag = 'v0.2.0-windows';
  const directory = path.join(process.env.RUNNER_TEMP, 'runtime-package');
  let release = (await github.rest.repos.listReleases({owner, repo, per_page: 100})).data.find(x => x.tag_name === tag);
  if (release && !release.draft) {
    core.notice('Published runtime assets are immutable; skipping upload.');
    return;
  }
  if (!release) release = (await github.rest.repos.createRelease({owner, repo, tag_name: tag, target_commitish: context.sha, name: 'Egress Workbench Windows 0.2.0 Preview', body: 'Verified runtime staged; Windows packages are being checked.', draft: true, prerelease: true})).data;
  let assets = (await github.rest.repos.listReleaseAssets({owner, repo, release_id: release.id})).data;
  for (const name of fs.readdirSync(directory)) {
    const data = fs.readFileSync(path.join(directory, name));
    const digest = 'sha256:' + crypto.createHash('sha256').update(data).digest('hex');
    const previous = assets.find(asset => asset.name === name);
    if (previous && previous.digest === digest) continue;
    if (previous) await github.rest.repos.deleteReleaseAsset({owner, repo, asset_id: previous.id});
    await github.rest.repos.uploadReleaseAsset({owner, repo, release_id: release.id, name, data, headers: {'content-type': name.endsWith('.json') ? 'application/json' : 'application/octet-stream', 'content-length': data.length}});
  }
  core.notice('Verified native runtime staged in draft release.');
};
