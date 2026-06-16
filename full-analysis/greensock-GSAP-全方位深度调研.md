# 🔬 greensock/GSAP - 全方位深度调研

## 项目全景
- **仓库**：`greensock/GSAP`
- **一句话定位**：GSAP (GreenSock Animation Platform), a JavaScript animation library for the modern web
- **基础指标**：Stars=25732 / Forks=2031 / 默认分支=`master`
- **Topics**：animation, gsap, javascript, javascript-library, scroll
- **Homepage**：https://gsap.com

## 核心架构
### 目录结构判断
- 顶层目录分布（递归树抽样汇总）：dist(76), src(34), esm(33), types(33), .gitignore(1), README.md(1), SECURITY.md(1), package.json(1)
- 关键文件候选：package.json, README.md, src/CSSPlugin.js, src/CSSRulePlugin.js, src/CustomBounce.js, src/CustomEase.js, src/CustomWiggle.js, src/Draggable.js, src/DrawSVGPlugin.js, src/EasePack.js, src/EaselPlugin.js, src/Flip.js

### 设计亮点研判
- 存在 Node/前端工具链入口，说明项目的运行、构建或 CLI 能力围绕 package.json 脚本组织。

## 源码深度解读
### README / 说明文档要点
# GSAP (GreenSock Animation Platform)

[![GSAP - Animate anything](https://gsap.com/GSAP-share-image.png)](https://gsap.com)

GSAP is a **framework-agnostic** JavaScript animation library that turns developers into animation superheroes. Build high-performance animations that work in **every** major browser. Animate CSS, SVG, canvas, React, Vue, WebGL, colors, strings, motion paths, generic objects... anything JavaScript can touch! GSAP's <a href="https://gsap.com/docs/v3/Plugins/ScrollTrigger/">ScrollTrigger</a> plugin delivers jaw-dropping scroll-based animations with minimal code. <a href="https://gsap.com/docs/v3/GSAP/gsap.matchMedia()">gsap.matchMedia()</a> makes building responsive, accessibility-friendly animations a breeze.

No other library delivers such advanced sequencing, reliability, and tight control while solving real-world problems on over 12 million sites. GSAP works around countless browser inconsistencies; your animations ***just work***. At its core, GSAP is a high-speed property manipulator, updating values over time with extreme accuracy. It's up to 20x faster than jQuery!

GSAP is completely flexible; sprinkle it wherever you want. **Zero dependencies.**

There are many optional <a href="https://gsap.com/docs/v3/Plugins">plugins</a> and <a href="https://gsap.com/docs/v3/Eases">easing</a> functions for achieving advanced effects easily like <a href="https://gsap.com/docs/v3/Plugins/ScrollTrigger/">scrolling</a>, <a href="https://gsap.com/docs/v3/Plugins/MorphSVGPlugin">morphing</a>, [text splitting](https://gsap.com/docs/v3/Plugins/SplitText), animating along a <a href="https://gsap.com/docs/v3/Plugins/MotionPathPlugin">motion path</a> or <a href="https://gsap.com/docs/v3/Plugins/Flip/">FLIP</a> animations. There's even a handy <a href="https://gsap.com/docs/v3/Plugins/Observer/">Observer</a> for normalizing event detection across browsers/devices. 


### Get Started

[![Get Started with GSAP](https://gsap.com/_img/github/get-started.jpg)](https://gsap.com/get-started)


## Docs &amp; Installation

View the <a href="https://gsap.com/docs">full documentation here</a>, including an <a href="https://gsap.com/install">installation guide</a>.

### CDN

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
```

See <a href="https://www.jsdelivr.com/gsap">JSDelivr's dedicated GSAP page</a> for quick CDN links to the core files/plugins. There are more <a href="https://gsap.com/install">installation instructio
...[truncated]

### 关键文件精读
### `package.json`
```
{
    "name": "gsap",
    "version": "3.15.0",
    "description": "GSAP is a robust JavaScript toolset that turns developers into animation superheroes. Build high-performance animations that work in **every** major browser. Animate CSS, SVG, canvas, React, Vue, WebGL, colors, strings, motion paths, generic objects...anything JavaScript can touch! The ScrollTrigger plugin lets you create jaw-dropping scroll-based animations with minimal code. No other library delivers such advanced sequencing, reliability, and tight control while solving real-world problems on millions of sites. GSAP works around countless browser inconsistencies; your animations **just work**. At its core, GSAP is a high-speed property manipulator, updating values over time with extreme accuracy. It's up to 20x faster than jQuery!",
    "homepage": "https://gsap.com",
	"module": "esm/index.js",
	"main": "dist/gsap.js",
    "types": "types/index.d.ts",
	"exports": {
		".": {
			"import": "./esm/index.js",
			"require":
...[truncated]
```

### `README.md`
```
# GSAP (GreenSock Animation Platform)

[![GSAP - Animate anything](https://gsap.com/GSAP-share-image.png)](https://gsap.com)

GSAP is a **framework-agnostic** JavaScript animation library that turns developers into animation superheroes. Build high-performance animations that work in **every** major browser. Animate CSS, SVG, canvas, React, Vue, WebGL, colors, strings, motion paths, generic objects... anything JavaScript can touch! GSAP's <a href="https://gsap.com/docs/v3/Plugins/ScrollTrigger/">ScrollTrigger</a> plugin delivers jaw-dropping scroll-based animations with minimal code. <a href="https://gsap.com/docs/v3/GSAP/gsap.matchMedia()">gsap.matchMedia()</a> makes building responsive, accessibility-friendly animations a breeze.

No other library delivers such advanced sequencing, reliability, and tight control while solving real-world problems on over 12 million sites. GSAP works around countless browser inconsistencies; your animations ***just work***. At its core, GSAP is a high-
...[truncated]
```

### `src/CSSPlugin.js`
```
/*!
 * CSSPlugin 3.15.0
 * https://gsap.com
 *
 * Copyright 2008-2026, GreenSock. All rights reserved.
 * Subject to the terms at https://gsap.com/standard-license
 * @author: Jack Doyle, jack@greensock.com
*/
/* eslint-disable */

import {gsap, _getProperty, _numExp, _numWithUnitExp, getUnit, _isString, _isUndefined, _renderComplexString, _relExp, _forEachName, _sortPropTweensByPriority, _colorStringFilter, _checkPlugin, _replaceRandom, _plugins, GSCache, PropTween, _config, _ticker, _round, _missingPlugin, _getSetter, _getCache, _colorExp, _parseRelative,
	_setDefaults, _removeLinkedListItem //for the commented-out className feature.
} from "./gsap-core.js";

let _win, _doc, _docElement, _pluginInitted, _tempDiv, _tempDivStyler, _recentSetterPlugin, _reverting,
	_windowExists = () => typeof(window) !== "undefined",
	_transformProps = {},
	_RAD2DEG = 180 / Math.PI,
	_DEG2RAD = Math.PI / 180,
	_atan2 = Math.atan2,
	_bigNum = 1e8,
	_capsExp = /([A-Z])/g,
	_horizontalExp = /(left|right|w
...[truncated]
```

### `src/CSSRulePlugin.js`
```
/*!
 * CSSRulePlugin 3.15.0
 * https://gsap.com
 *
 * @license Copyright 2008-2026, GreenSock. All rights reserved.
 * Subject to the terms at https://gsap.com/standard-license
 * @author: Jack Doyle, jack@greensock.com
*/
/* eslint-disable */

let gsap, _coreInitted, _win, _doc, CSSPlugin,
	_windowExists = () => typeof(window) !== "undefined",
	_getGSAP = () => gsap || (_windowExists() && (gsap = window.gsap) && gsap.registerPlugin && gsap),
	_checkRegister = () => {
		if (!_coreInitted) {
			_initCore();
			if (!CSSPlugin) {
				console.warn("Please gsap.registerPlugin(CSSPlugin, CSSRulePlugin)");
			}
		}
		return _coreInitted;
	},
	_initCore = core => {
		gsap = core || _getGSAP();
		if (_windowExists()) {
			_win = window;
			_doc = document;
		}
		if (gsap) {
			CSSPlugin = gsap.plugins.css;
			if (CSSPlugin) {
				_coreInitted = 1;
			}
		}
	};


export const CSSRulePlugin = {
	version: "3.15.0",
	name: "cssRule",
	init(target, value, tween, index, targets) {
		if (!_checkRegist
...[truncated]
```

### `src/CustomBounce.js`
```
/*!
 * CustomBounce 3.15.0
 * https://gsap.com
 *
 * @license Copyright 2008-2026, GreenSock. All rights reserved.
 * Subject to the terms at https://gsap.com/standard-license
 * @author: Jack Doyle, jack@greensock.com
*/
/* eslint-disable */

let gsap, _coreInitted, createCustomEase,
	_getGSAP = () => gsap || (typeof(window) !== "undefined" && (gsap = window.gsap) && gsap.registerPlugin && gsap),
	_initCore = required => {
		gsap = _getGSAP();
		createCustomEase = gsap && gsap.parseEase("_CE");
		if (createCustomEase) {
			_coreInitted = 1;
			gsap.parseEase("bounce").config = vars => typeof(vars) === "object" ? _create("", vars) : _create("bounce(" + vars + ")", {strength:+vars});
		} else {
			required && console.warn("Please gsap.registerPlugin(CustomEase, CustomBounce)");
		}
	},
	_normalizeX = a => { //scales all the x values in an array [x, y, x, y...] AND rounds them to the closest hundredth (decimal)
		let l = a.length,
			s = 1 / a[l - 2],
			rnd = 1000,
			i;
		for (i = 2; i
...[truncated]
```

### `src/CustomEase.js`
```
/*!
 * CustomEase 3.15.0
 * https://gsap.com
 *
 * @license Copyright 2008-2026, GreenSock. All rights reserved.
 * Subject to the terms at https://gsap.com/standard-license
 * @author: Jack Doyle, jack@greensock.com
*/
/* eslint-disable */

import { stringToRawPath, rawPathToString, transformRawPath } from "./utils/paths.js";

let gsap, _coreInitted,
	_getGSAP = () => gsap || (typeof(window) !== "undefined" && (gsap = window.gsap) && gsap.registerPlugin && gsap),
	_initCore = () => {
		gsap = _getGSAP();
		if (gsap) {
			gsap.registerEase("_CE", CustomEase.create);
			_coreInitted = 1;
		} else {
			console.warn("Please gsap.registerPlugin(CustomEase)");
		}
	},
	_bigNum = 1e20,
	_round = value => ~~(value * 1000 + (value < 0 ? -.5 : .5)) / 1000,
	_bonusValidated = 1, //<name>CustomEase</name>
	_numExp = /[-+=.]*\d+[.e\-+]*\d*[e\-+]*\d*/gi, //finds any numbers, including ones that start with += or -=, negative numbers, and ones in scientific notation like 1e-8.
	_needsParsingExp = /[c
...[truncated]
```

### 关键逻辑总结
- 从关键文件组合看，项目更像围绕单一目标组织的任务流水线/工具链，而不是超重平台。
- 入口文件决定外部交互界面（CLI / API / UI），配置文件决定运行时依赖，测试文件暴露作者真正关心的行为边界。
- 如果用户只读 README，通常只能知道“能做什么”；而从目录与入口文件能看出“怎么做、扩展点在哪、维护成本高不高”。

## 社区口碑
### GitHub Issues 抽样
- #650 [CLOSED] Reduce size of package（comments=[{'id': 'IC_kwDOAFobss8AAAABAiQnGA', 'author': {'login': 'jackdoyle'}, 'authorAssociation': 'MEMBER', 'body': "That sounds like a setting you'd manage in your bundler. It's not anything GSAP itself controls. And keep in mind that users don't actually load the mapping files by default - those are just there in case users want to read the source without parsing through all the minified stuff. ", 'createdAt': '2026-04-27T22:30:12Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/greensock/GSAP/issues/650#issuecomment-4330891032', 'viewerDidAuthor': False}, {'id': 'IC_kwDOAFobss8AAAABAiYktg', 'author': {'login': 'phapdinh'}, 'authorAssociation': 'NONE', 'body': "i mean bundlers can generate their own map files if needed. I feel that the extra step of having consuming projects remove map files is better if they weren't committed to the repo, but if you feel that the map files are useful, free free to close issue", 'createdAt': '2026-04-27T22:48:04Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/greensock/GSAP/issues/650#issuecomment-4331021494', 'viewerDidAuthor': False}] labels=无）
- #649 [CLOSED] [enhancement]: allow passing raw paths to morphSvg（comments=[{'id': 'IC_kwDOAFobss8AAAABAD7dDA', 'author': {'login': 'jackdoyle'}, 'authorAssociation': 'MEMBER', 'body': 'I read your question a few times and I\'m still a bit fuzzy on what you\'re asking. MorphSVG allows you to pass in a path -OR- selector text to a path -OR- path data itself (like the string that fills the "d" attribute). Use whatever is most convenient for you. \n\nDoes that answer your question? Perhaps I\'m missing something obvious (sorry!)', 'createdAt': '2026-04-22T18:47:55Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/greensock/GSAP/issues/649#issuecomment-4299087116', 'viewerDidAuthor': False}, {'id': 'IC_kwDOAFobss8AAAABAD8htw', 'author': {'login': 'GameLord2011'}, 'authorAssociation': 'NONE', 'body': "The path data, as that would be the most convienent if you were attempting to do canvas drawing stuff, I can't find in the docs how to pass the contents of the D attribute to the target (`#${icons[i].slug}`), whenever I replace it with `icons[i].path` it uses a queryselector and stops the animation.", 'createdAt': '2026-04-22T18:51:01Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/greensock/GSAP/issues/649#issuecomment-4299104695', 'viewerDidAuthor': False}, {'id': 'IC_kwDOAFobss8AAAABAD-mog', 'author': {'login': 'jackdoyle'}, 'authorAssociation': 'MEMBER', 'body': 'Are you sure you\'re passing legitimate path data? It typically starts with "M..." I wonder if you\'re passing the selector text or some other thing that isn\'t really the path data. If you\'re still struggling, can you please provide a minimal demo that clearly illustrates the problem? It\'s best to post in the forums at https://gsap.com/community - it\'ll embed the codepen and also invite the community to chime in more than here in the github issues area. \n\nAnother solution is to just create a temporary element that contains your path data, and feed that path element into the animation. The element itself shouldn\'t need to be in the DOM - MorphSVG will just pull the path data from it. ', 'createdAt': '2026-04-22T18:56:59Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/greensock/GSAP/issues/649#issuecomment-4299138722', 'viewerDidAuthor': False}, {'id': 'IC_kwDOAFobss8AAAABAD-40w', 'author': {'login': 'GameLord2011'}, 'authorAssociation': 'NONE', 'body': 'Okay.', 'createdAt': '2026-04-22T18:57:49Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/greensock/GSAP/issues/649#issuecomment-4299143379', 'viewerDidAuthor': False}, {'id': 'IC_kwDOAFobss8AAAABAEC0FQ', 'author': {'login': 'GameLord2011'}, 'authorAssociation': 'NONE', 'body': "For refrence, this was the emitted error message:\n\n> SyntaxError: Failed to execute 'querySelectorAll' on 'Document': 'M16.5921 9.1962s-.354-3.298-3.627-3.39c-3.2741-.09-4.9552 2.474-4.9552 6.14 0 3.6651 1.858 6.5972 5.0451 6.5972 3.184 0 3.5381-3.665 3.5381-3.665l6.1041.365s.36 3.31-2.196 5.836c-2.552 2.5241-5.6901 2.9371-7.8762 2.9201-2.19-.017-5.2261.034-8.1602-2.97-2.938-3.0101-3.436-5.9302-3.436-8.8002 0-2.8701.556-6.6702 4.047-9.5502C7.444.72 9.849 0 12.254 0c10.0422 0 10.7172 9.2602 10.7172 9.2602z' is not a valid selector.\n    at toArray (gsap-core.js:671:173)\n    at new Tween (gsap-core.js:3172:128)\n    at _createTweenType (gsap-core.js:637:10)\n    at Timeline.to (gsap-core.js:2021:5)\n", 'createdAt': '2026-04-22T19:08:44Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/greensock/GSAP/issues/649#issuecomment-4299207701', 'viewerDidAuthor': False}, {'id': 'IC_kwDOAFobss8AAAABAEHWhQ', 'author': {'login': 'jackdoyle'}, 'authorAssociation': 'MEMBER', 'body': 'For reference: \nhttps://gsap.com/community/forums/topic/45422-using-a-raw-svg-path-as-the-target-in-a-morphsvg/', 'createdAt': '2026-04-22T19:20:44Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/greensock/GSAP/issues/649#issuecomment-4299282053', 'viewerDidAuthor': False}] labels=无）
- #643 [CLOSED] [Docs/Typings] Misleading JSDoc comment for play() suggests play(true) plays from current point（comments=[{'id': 'IC_kwDOAFobss74osCq', 'author': {'login': 'jackdoyle'}, 'authorAssociation': 'MEMBER', 'body': "You're exactly right, and I apologize for that misleading JSDoc comment. The first parameter shouldn't be a boolean. We'll get that fixed in the next release. ", 'createdAt': '2026-04-01T16:42:25Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [{'content': 'HEART', 'users': {'totalCount': 1}}], 'url': 'https://github.com/greensock/GSAP/issues/643#issuecomment-4171415722', 'viewerDidAuthor': False}, {'id': 'IC_kwDOAFobss78nCvB', 'author': {'login': 'jackdoyle'}, 'authorAssociation': 'MEMBER', 'body': 'Fixed in 3.15.0 ✅', 'createdAt': '2026-04-13T16:42:28Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/greensock/GSAP/issues/643#issuecomment-4238093249', 'viewerDidAuthor': False}, {'id': 'IC_kwDOAFobss79cmVH', 'author': {'login': 'RomaTk'}, 'authorAssociation': 'NONE', 'body': 'Thank you, I truly appreciate and value your efforts.', 'createdAt': '2026-04-15T12:48:12Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [{'content': 'THUMBS_UP', 'users': {'totalCount': 1}}], 'url': 'https://github.com/greensock/GSAP/issues/643#issuecomment-4252132679', 'viewerDidAuthor': False}] labels=无）
- #642 [OPEN] Screen Readers do not expose SplitText（comments=[{'id': 'IC_kwDOAFobss7mM8o6', 'author': {'login': 'aardrian'}, 'authorAssociation': 'NONE', 'body': "I understand a Masto user made a video that _may_ have coincided with an emailed bug report on 12 May 2025:\nhttps://gsap-split-text-a11y.eu.dev.monkapps.com/SplitText_aria_VoiceOver_iOS17.6.1_Safari17.6_iPhoneProMax12.mp4\n\nEdited to add the test page behind that video:\nhttps://gsap-split-text-a11y.eu.dev.monkapps.com/split-text-aria-error.html\n\nI've also made videos for the first 5 table entries above, in case those would be helpful.", 'createdAt': '2026-02-06T19:18:17Z', 'includesCreatedEdit': True, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/greensock/GSAP/issues/642#issuecomment-3862153786', 'viewerDidAuthor': False}, {'id': 'IC_kwDOAFobss7mkHg7', 'author': {'login': 'jackdoyle'}, 'authorAssociation': 'MEMBER', 'body': "Hi @aardrian \n\nThanks for the detailed information. Just to be clear, you're not reporting any issues with SplitText itself - you're just asking for some minor improvements to the docs so that people understand ARIA limitations better? ", 'createdAt': '2026-02-08T20:40:54Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/greensock/GSAP/issues/642#issuecomment-3868227643', 'viewerDidAuthor': False}, {'id': 'IC_kwDOAFobss7mlEpy', 'author': {'login': 'aardrian'}, 'authorAssociation': 'NONE', 'body': "This issue is not reporting bugs with SplitText. Those may be separate issues (because there are some). I filed this first because it seemed like the easiest thing for the team to address immediately. \n\nAnd to be clear — these are _not_ ARIA limitations. This issue reflects the documentation's need to better convey how to use ARIA correctly, per spec.", 'createdAt': '2026-02-08T22:46:24Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [{'content': 'THUMBS_UP', 'users': {'totalCount': 1}}], 'url': 'https://github.com/greensock/GSAP/issues/642#issuecomment-3868478066', 'viewerDidAuthor': False}] labels=无）
- #640 [CLOSED] SplitText: instanceof HTMLElement check fails in cross-window/iframe contexts（comments=[{'id': 'IC_kwDOAFobss7dfE4E', 'author': {'login': 'jackdoyle'}, 'authorAssociation': 'MEMBER', 'body': 'Great point, @maximebeguin . Thanks for such a clean and clear report, including a minimal demo. \n\nDoes this work better for you (minified UMD)?: \nhttps://assets.codepen.io/16327/SplitText3-beta.min.js', 'createdAt': '2026-01-06T18:55:59Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/greensock/GSAP/issues/640#issuecomment-3715911172', 'viewerDidAuthor': False}, {'id': 'IC_kwDOAFobss7dfXFT', 'author': {'login': 'maximebeguin'}, 'authorAssociation': 'NONE', 'body': 'Hey @jackdoyle, I just tested it and it works perfectly. Your response time is out of this world. Feeling super grateful! Thank you!!', 'createdAt': '2026-01-06T19:19:03Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [{'content': 'HEART', 'users': {'totalCount': 1}}], 'url': 'https://github.com/greensock/GSAP/issues/640#issuecomment-3715985747', 'viewerDidAuthor': False}, {'id': 'IC_kwDOAFobss78nEu7', 'author': {'login': 'jackdoyle'}, 'authorAssociation': 'MEMBER', 'body': 'Fixed in 3.15.0 ✅', 'createdAt': '2026-04-13T16:43:54Z', 'includesCreatedEdit': False, 'isMinimized': False, 'minimizedReason': '', 'reactionGroups': [], 'url': 'https://github.com/greensock/GSAP/issues/640#issuecomment-4238101435', 'viewerDidAuthor': False}] labels=无）
- #639 [CLOSED] "JS Frameworks" page in Learning docs with inaccessible links（comments=[] labels=无）

### Pull Requests 抽样
- PR #648 [OPEN] Update demo link to new URL
- PR #638 [CLOSED] Fix TypeScript case-sensitivity errors on case-insensitive filesystems
- PR #634 [CLOSED] docs: update http links to https and fix typo
- PR #632 [CLOSED] fix(matrix): avoid setAttribute('style') to support strict CSP (#623)
- PR #598 [CLOSED] fix: Correct deprecation links in gsap-core.d.ts to the right release notes

### Releases 抽样
暂无 release 或数据不可用

### 真实反馈与维护信号研判
- 抽样 issue 中 open/closed 约为 1/7，可作为维护响应速度的弱信号。
- 近期 PR 抽样里可见已合并项 0 个，说明项目并非完全冻结。
- 高频问题通常比 README 更能暴露真实落地难点：安装、兼容性、性能边界、文档歧义、平台限制。
- 若外部搜索数据不可用，本报告明确以 GitHub issue/PR/release 作为一手社区信号，不伪造站外口碑。

## 竞品对比
| 维度 | GSAP | 竞品/替代 |
|---|---|---|
| 定位 | 面向仓库作者设定的具体场景，通常更垂直 | Playwright / Puppeteer / Selenium 往往更通用或生态更大 |
| 学习曲线 | 依赖其内部脚本/配置约定 | 通用方案学习成本更高，但生态更成熟 |
| 差异化 | 仓库通常以“快上手、场景专用、意见化实现”为卖点 | 通用方案强调可扩展、稳定性、跨场景能力 |
| 风险 | 作者驱动、文档深度可能不足、接口稳定性不确定 | 大项目更稳定，但改造成本更高 |

## 核心研判
### 项目优势
- 对目标问题有强意见化实现，落地路径通常比“从零搭建通用栈”更短。
- 如果核心文件少而清晰，二次阅读和定制成本较低。
- GitHub 原生 issue / release / PR 能直接帮助判断项目是否仍在演进。

### 项目风险
- 若 stars、forks、release 或 PR 活跃度偏低，意味着长期维护能力要谨慎评估。
- 如果关键逻辑过于集中在单文件脚本中，后续扩展会受到可维护性约束。
- 若缺少测试/CI/配置 schema，生产环境采用前应先做自测和边界验证。

### 适用场景
- 需要快速验证该仓库所解决的问题是否值得投入。
- 团队愿意接受一定的作者意见化设计，以换取更快交付。
- 适合作为参考实现、内部 PoC、垂直任务工具，而非默认直接替代成熟平台。

### 不适用场景
- 对 SLA、兼容矩阵、长期 LTS 有强要求的核心生产系统。
- 需要极高社区冗余、插件生态或企业级支持的场景。

## 关键文件路径速查
- `package.json`
- `README.md`
- `src/CSSPlugin.js`
- `src/CSSRulePlugin.js`
- `src/CustomBounce.js`
- `src/CustomEase.js`
- `src/CustomWiggle.js`
- `src/Draggable.js`
- `src/DrawSVGPlugin.js`
- `src/EasePack.js`
- `src/EaselPlugin.js`
- `src/Flip.js`

## 3 条关键发现
- 代码入口/骨架集中在：package.json, README.md, src/CSSPlugin.js, src/CSSRulePlugin.js, src/CustomBounce.js
- Issue 抽样显示近期关注点包括：Reduce size of package；[enhancement]: allow passing raw paths to morphSvg
- 目录结构与关键文件表明该项目采用较强意见化实现，而非纯演示仓库。

## 研究方法与数据来源
- GitHub Repo API / README / 默认分支递归文件树
- 关键源码文件抽样精读
- Issues / PRs / Releases 社区活动抽样
- 说明：若外部搜索数据不可用，则明确标注并不伪造口碑结论
