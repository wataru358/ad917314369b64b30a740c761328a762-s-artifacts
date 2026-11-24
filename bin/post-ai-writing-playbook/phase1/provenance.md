# Phase 1 provenance

Source paths are relative to the original repository and establish provenance. Use the bundled rules and the current run’s artifacts during execution. The SHA-256 hashes correspond to the original file bytes read when building the package. Historical cohort counts and run IDs in the original bundled settings document provenance. Derive counts from the new run.

| Original file | Original SHA-256 | Purpose |
| --- | --- | --- |
| `bin/analytics/post-ai-writing/a01-settings.json` | `e892ea00a23fef71cbed36aebf4b7586e092bcc36268bb1124a8a115c8a5778c` | references/a01-settings.json |
| `bin/analytics/post-ai-writing/a02-settings.json` | `ee32b3d6a292fdee6e47d01585505c1c46ed870d8b4d01e8545e9a1e579cfaa2` | references/a02-settings.json |
| `bin/analytics/post-ai-writing/a03-settings.json` | `318530ead2a0f127f03227a5489ae83803c79e64a32139b47b411425a4c23534` | references/a03-settings.json |
| `bin/analytics/post-ai-writing/a04-settings.json` | `ed4b0493ab204ce93b0217abbed0ecf685774fbd3d43aa40e0fc3f4c123708d0` | references/a04-settings.json |
| `bin/analytics/post-ai-writing/a05-settings.json` | `e1d6adc5c50d35ec61b50c624582bc68c77a43510c1fded23f2fda8f3c3a73d5` | references/a05-settings.json |
| `bin/analytics/post-ai-writing/a06-settings.json` | `ad1781340e935ca058fdc83ab7d849d03351a8de7bf999954185e86e6e80ba29` | references/a06-settings.json |
| `bin/analytics/post-ai-writing/a07-content-rules-v1.json` | `21331b571da8b05db86e628b677e16903e616514977a4bb24ca4d79f0171296e` | references/a07-content-rules-v1.json (portable rubric link and replay state) |
| `bin/analytics/post-ai-writing/a07-proxy-settings-v1.json` | `2f63e2d0c5f312c893bf9b22a48d68e244968effb4223df6d012a08bbee6fd45` | references/a07-proxy-settings-v1.json (portable methods link) |
| `bin/analytics/post-ai-writing/a07-sample-settings.json` | `0a7ea2894df9e6e005a5674f980bf35edb3e28c10a2ba37d8a3540d29f57d7fe` | references/a07-sample-settings.json |
| `bin/analytics/post-ai-writing/analysis/00-分析準備と英語集合.md` | `5a46cabbc45a92838926d2560fe2d56477e56d66bdfc677f59b1d34541a8fcaf` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/analysis/01-記事と段落の長さ.md` | `3ebb346fe81a23335aedfcf832d353e840eb8fedb54ba1425df2f16f01466685` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/analysis/02-文のリズムと句読法.md` | `13f015a3d106be993d1b323a43b50393916500117124b927a15af238b8c97e29` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/analysis/03-箇条書きと太字と見出し.md` | `010aff6b6f398878d8bf0830aafc337dc3db8e0df05422bebddca85ae2118cb1` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/analysis/04-増えた語と減った語.md` | `e778f9901b517d47fa65fd084288d8f877018098e99d213bee57dc25ea6c1268` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/analysis/05-書き手の声と読者への呼びかけ.md` | `e6bf269f4ccd17102a36e5de88fddfa547d9637e831733f82769baad7d893807` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/analysis/06-記事構成の定型化.md` | `c6598dfd896eec6cc4529d60fd59869ea1afb26debe063b28e25c6e677a3f3c7` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/analysis/07-経験談と具体的な検証記述.md` | `4b747461b19610b5cc6fcc043b0407508455987a6f4a9312f4917e223914d6a0` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/analysis/08-コードと説明文の関係.md` | `063ce6df419adbf510621518872832066d6efbe0920a23b2fe3e78a3f01c3c85` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/analysis/09-話題と書き手の入れ替わり.md` | `d78f9b9efa624b52b9be726f94eda4244379acff4a4183633fe93a36802fa3ec` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/analysis/10-変化が始まった時期.md` | `7e60b8095b0a52937022b743b8c53c931c8e48fe838fb67e16c70ace692fbd00` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/analysis/11-条件を変えた再分析.md` | `0c521b2db7bb8b24b6d1d62ee0120fc32d6b881e6e0203cccc6ae3aa33415304` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/analysis/12-日本語記事に向けた結果整理.md` | `59c6fb5afa918a187c1917b79d314df0a3c6933b79ceabb7c2a8a4fbe526a21a` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/analysis/13-答えに届くまでの距離.md` | `3fcd3ff1ac37ecfe5428a0b1a75e865619c23ced1c16fbf9a2726cfc9324bc8b` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/analysis/14-文体の多様性と変化の偏り.md` | `8d15a2ce34602d6038d5c63428589e196bbbdf5f6608729e1bc82da4e7d045bf` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/analysis/A04-比較方法.md` | `70fc8c42d6b21aae2698cf0050e887bca91d91a50081aa00aba5cfa2dee1ff7b` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/analysis/A04-測定上の注意.md` | `794287d57dca34af4e75af470c141c07797fa0f4343202980fbf175b0986417b` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/analysis/A05-比較方法.md` | `5f4f17ef9975e19cc2df3bc0f5326419a7c63370d6f5935cf08cca30556cbf56` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/analysis/A06-比較方法.md` | `5ce419330eae8405efefc4670e242768da14595afc9b1b47141c4331c401924e` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/analysis/A07-全128記事の使用方針と代理対応点検.md` | `366b8fa6aa9f5c7b28f033d37c63c3bc7ce2847eaee8f28afb8490d32faf4dd1` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/analysis/A07-内容判定基準.md` | `0d28618a29be055a3f8f588cfc0147647cbe7024fe681f8305fd47e29ed52832` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/analysis/A07-再評価32記事の差分解決完了.md` | `b67d28b483b62d5889267aa1027465216625e13f6b4f4aebf40ffb092f667f86` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/analysis/T01-実行結果.md` | `c4bea825e528bb6759807dd035cdb3315418bb791ce705fafa276686c95be157` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/analysis/T02-全量特徴量の実行結果.md` | `e871322ff3b763211a8a940bbc1f4459fa67f5e524703ae7ee17ba6b9d25701d` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/analysis/T02-分割校正の実行結果.md` | `aafc57e2b54674ad0857aeb377c9a394323b56ebec86e9a06777fecc8df6e1a6` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/analysis/T03-対象統計の実行結果.md` | `3d56aaa8ae984a50e7a7f921f248c27ae0ebce84643777ee82734757a93f096b` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/analysis/status.json` | `d53350ce3a3fce8568429d8aca9359c3a9b5dafd43b767c1f13fe110051805eb` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/analysis/測定定義.md` | `9e4071025b21059f609e5710bdd232a865c4b9d9c921c8260d967d27660781dd` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/article_extraction.py` | `88709aaec5781597f56af75f1487ef870fb1961e3a0472a2973bace4c4f98584` | references/article_extraction.py |
| `bin/analytics/post-ai-writing/data/analysis/dev-writing-handoffs/20261030T075140Z-99fc69fcc076/A10-session-20261104T174542Z/accepted-methods.json` | `ddc22b60dcae61b423fa1635ac603eb48ff7d043d24b3d0343c1e46a74594b19` | references/a10-methods.json (method fields) |
| `bin/analytics/post-ai-writing/data/analysis/dev-writing-handoffs/20261030T075140Z-99fc69fcc076/A11-session-20261105T073145Z/S02-synthesis/strengthened-contract.json` | `77b800797fab4dd87ecd78970cb8e509d51078cb0a609f3e831cfd18aa766449` | A11 coding and acceptance in analysis-methods.md |
| `bin/analytics/post-ai-writing/data/analysis/dev-writing-v1/20261030T075140Z-99fc69fcc076/A08/aggregation-v1/frozen-config.json` | `7ce76ff6d90af80e87d99c6eea0f9f8766d9a257ebc934631cc83a78e7374a99` | references/a08-aggregation.json (method fields) |
| `bin/analytics/post-ai-writing/data/analysis/dev-writing-v1/20261030T075140Z-99fc69fcc076/A08/full-counts-v1/rules-v2.md` | `f86a1aa5d425bcd30af63224f1ab15e5c034a1c4dd64ffe77c10387aa729df22` | references/a08-code-rules.md (expanded for full-cohort processing and adapted to the replay DAG) |
| `bin/analytics/post-ai-writing/data/analysis/dev-writing-v1/20261030T075140Z-99fc69fcc076/A09/ai-topic-v1/config.json` | `e1da040f652cfd305ca5524121e1beff8f67c2bd63ccd83a838449f49ff82c11` | references/a09-ai-topic.json (lexical rules) |
| `bin/analytics/post-ai-writing/data/analysis/dev-writing-v1/20261030T075140Z-99fc69fcc076/A09/preparation-v1/methods.md` | `53cc1088aecc7cc9ffcb02a74ebf6a5b03ed5de0515106c5610576260557e66c` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/data/analysis/dev-writing-v1/20261030T075140Z-99fc69fcc076/A10/preparation-v1/methods.md` | `8567932184c64c4b1f89cc4fcb4a46d62fd674711d0b9356598d6bd9c9824354` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/data/analysis/dev-writing-v1/20261030T075140Z-99fc69fcc076/A10/time-models-v2/methods.md` | `2d67737a0b9c592316a09f0649ba5acc09dd93f6d214350c5d2ccf5db642baa0` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/data/analysis/dev-writing-v1/20261030T075140Z-99fc69fcc076/A11/report-ja.md` | `a705750a9a77391bea910f99f85de7eb1a076fcac4f21d8433382793ada0aa36` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/data/analysis/dev-writing-v1/20261030T075140Z-99fc69fcc076/A12/analysis-v1/contract.json` | `7cb91c4512624e048f4cc6f79ab2845ecde749cafa0b38682274f3e78dbd1efd` | references/a12-distance.json |
| `bin/analytics/post-ai-writing/data/analysis/dev-writing-v1/20261030T075140Z-99fc69fcc076/R01/README.md` | `da2ece7202e67a49f4e4011e6f837b57c83a5424cfb23c2c84169ef62e57eb21` | reporting and scope contract |
| `bin/analytics/post-ai-writing/data/analysis/dev-writing-v1/20261030T075140Z-99fc69fcc076/R01/report-ja.md` | `8ac4762318e5b67919ba91d714fe2ea2152e874c509784ea64db7e7066381c82` | reporting and scope contract |
| `bin/analytics/post-ai-writing/data/analysis/dev-writing-v1/20261030T075140Z-99fc69fcc076/V01/analysis-v1/frozen-config.json` | `79a70d7c65c922f94afc39e95c2c88728c3df22368cebf9b81dff9f506fc8b4f` | references/v01-variants.json (metrics and planned conditions) |
| `bin/analytics/post-ai-writing/data/analysis/dev-writing-v1/20261030T075140Z-99fc69fcc076/feature-rules.json` | `f7c01c5c2a03f6e3bfbead64c91656f596a2b653d06376efefd4ea2e93f3d6a8` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/data/analysis/dev-writing-v1/20261030T075140Z-99fc69fcc076/language-rules.json` | `d34ad97617a72a2b19056255bc3afca0cb1b929e18305becacf18c7827091717` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/data/analysis/dev-writing-v1/20261030T075140Z-99fc69fcc076/segmentation-rules.json` | `443cb8f36dfac6544562b45bdd7028e0e2f2240c2617a22b4f3b802ae1b2ba38` | Phase 1 task or method specification |
| `bin/analytics/post-ai-writing/language_cohort.py` | `8078e085947028d275a6423e9a2fa11ba9e871761802a0d87f6d89026e25a290` | references/language_rules.py (portable excerpt, compressed SQLite field replaced by parsed payload) |
| `bin/analytics/post-ai-writing/pyproject.toml` | `3cb78bbc38e7852c06a673f455b632eef030a3d9ef55f08cad3975b3fefc66ed` | measurement-spec.md |
| `bin/analytics/post-ai-writing/segmentation.py` | `bb967de85bee8eb2496d6580110d464243892397a049b5a99e7a07c7e36e31ed` | references/segmentation.py (portable excerpt) |
| `bin/analytics/post-ai-writing/t02-strata-map.json` | `04c420ad1e0658386fb27cffdee4959198d319434b147afbd199fa1ae4f1d196` | references/t02-strata-map.json |
| `bin/analytics/post-ai-writing/t02_classification.json` | `96a659ed1de28eb1400ba29510853061526555e1321bdbfb60add575b4c545a8` | references/t02_classification.json |
| `bin/analytics/post-ai-writing/t02_controls.json` | `79d3c12a9a2770d40cf27c617b748ae4e655e61b41aa737dba16fa46adf902d6` | references/t02_controls.json |
| `bin/analytics/post-ai-writing/t02_structure.py` | `67171f21fba41acf8e47c97c0b8114cf24c0a0f1268e0f48ff50bb28e32214bf` | references/t02_structure.py |
| `bin/analytics/post-ai-writing/t03-settings.json` | `75d00da768b8a6ac7229bd8abac5cd886263cbcb357a31aec7fe62daa37f7828` | references/t03-settings.json |
| `bin/analytics/post-ai-writing/t02_metadata.py` | `108b77f9b0c70deb1827770f5df6fa7cbd4c35b5dfa8a8828e64a2eaad0ac911` | references/t02_metadata.py |
| `bin/analytics/post-ai-writing/t02_metadata_v2.py` | `f2d36f1837079758e94784aa4b2a4b6d5370f423434ae4e17f0d946d0f089415` | references/t02_metadata_v2.py |
| `bin/analytics/post-ai-writing/t02_features.py` | `f135cbbead51fc2489bbb94579c78d17357d0a7f94d4d552f043909f549dd756` | references/t02_features.py |
| `bin/analytics/post-ai-writing/data/analysis/dev-writing-handoffs/20261030T075140Z-99fc69fcc076/A11-session-20261105T073145Z/S03-calibration-fix-v2/candidate-dictionary.json` | `6d4c067ca8a1b894832b9a78ce8282a5ed2dce4b6e94dffdea4a888ee0d640f9` | references/a11-candidate-dictionary.json |
| `bin/analytics/post-ai-writing/data/analysis/dev-writing-handoffs/20261030T075140Z-99fc69fcc076/A11-session-20261105T073145Z/S03-calibration-fix-v2/rubric-draft.md` | `9eea0656f76891a7b22a2c944af769e31133ab804aeb9098150155053e714e27` | references/a11-rubric.md |
| `bin/analytics/post-ai-writing/data/analysis/dev-writing-handoffs/20261030T075140Z-99fc69fcc076/A11-session-20261105T073145Z/S03-alignment-pilot/align_pilot.py` | `7f8e3035a79e4321e5fce9c8310c19d7334972649990c82a996dd2394b7fafb1` | Porting specification for A11 DOM/S positions |
