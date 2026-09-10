import json

from PIL import Image, ImageDraw

from rastalr_pipeline import core


def test_small_batch_runs_through_pending_qa_catalog_and_contact_sheet(tmp_path, monkeypatch):
    root = tmp_path
    for directory in ("metadata", "source/generated/incoming", "staging/pending/raw", "staging/pending/normalized", "previews/contact_sheets"):
        (root / directory).mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(core, "ROOT", root)
    monkeypatch.setattr(core, "MANIFEST_PATH", root / "metadata/manifest.json")
    monkeypatch.setattr(core, "CATALOG_PATH", root / "metadata/catalog.csv")
    monkeypatch.setattr(core, "QA_JSON_PATH", root / "metadata/qa_report.json")
    monkeypatch.setattr(core, "QA_MD_PATH", root / "metadata/qa_report.md")
    monkeypatch.setattr(core, "QA_CSV_PATH", root / "metadata/qa_report.csv")
    monkeypatch.setattr(core, "CONTACT_SHEET_PATH", root / "previews/contact_sheets/pilot_pending.png")

    image = Image.new("RGBA", (12, 12), (0, 0, 0, 0))
    ImageDraw.Draw(image).rectangle((3, 3, 8, 8), fill=(104, 162, 154, 255))
    image.save(root / "source/generated/incoming/monitor.png")
    batch = {"assets": [{"source": "source/generated/incoming/monitor.png", "category": "icu", "asset_type": "patient_monitor_floor", "footprint_width_tiles": 1, "footprint_height_tiles": 1}]}
    (root / "metadata/pilot_batch.json").write_text(json.dumps(batch), encoding="utf-8")

    assets = core.ingest_batch("metadata/pilot_batch.json")
    assert assets[0]["filename"] == "patient_monitor_floor_01.png"
    assert core.normalize_pending(padding=2) == ["patient_monitor_floor_01"]
    report = core.run_qa()
    assert report["status_counts"] == {"pass": 1}
    assert core.write_catalog().is_file()
    assert core.create_contact_sheet(scale=1).is_file()
    assert Image.open(core.create_contact_sheet()).size == (2880, 672)
    manifest = json.loads((root / "metadata/manifest.json").read_text(encoding="utf-8"))
    assert manifest["assets"][0]["approval_status"] == "needs_human_review"
    assert manifest["assets"][0]["source_scale"] == 1
    assert (manifest["assets"][0]["canvas_width"], manifest["assets"][0]["canvas_height"]) == (10, 10)
    assert core.approve_assets(["patient_monitor_floor_01"]) == ["patient_monitor_floor_01"]
    approved = core.load_manifest()["assets"][0]
    assert approved["approval_status"] == "approved"
    assert (root / approved["approved_staging_path"]).is_file()
    assert (root / approved["final_path"]).is_file()


def test_pipeline_records_native_dimensions_after_eight_x_source_scale(tmp_path, monkeypatch):
    root = tmp_path
    for directory in ("metadata", "source/generated/incoming", "staging/pending/raw", "staging/pending/normalized", "previews/contact_sheets"):
        (root / directory).mkdir(parents=True, exist_ok=True)
    for name, path in {
        "ROOT": root, "MANIFEST_PATH": root / "metadata/manifest.json", "CATALOG_PATH": root / "metadata/catalog.csv",
        "QA_JSON_PATH": root / "metadata/qa_report.json", "QA_MD_PATH": root / "metadata/qa_report.md",
        "QA_CSV_PATH": root / "metadata/qa_report.csv", "CONTACT_SHEET_PATH": root / "previews/contact_sheets/pilot_pending.png",
    }.items():
        monkeypatch.setattr(core, name, path)
    image = Image.new("RGBA", (96, 96), (0, 0, 0, 0))
    ImageDraw.Draw(image).rectangle((16, 16, 79, 79), fill=(104, 162, 154, 255))
    image.save(root / "source/generated/incoming/working_scale.png")
    batch = {"assets": [{"source": "source/generated/incoming/working_scale.png", "category": "icu", "asset_type": "patient_monitor_floor", "source_scale": 8}]}
    (root / "metadata/pilot_batch.json").write_text(json.dumps(batch), encoding="utf-8")
    core.ingest_batch("metadata/pilot_batch.json")
    core.normalize_pending()
    manifest = core.load_manifest()
    asset = manifest["assets"][0]
    assert asset["source_scale"] == 8
    assert (asset["canvas_width"], asset["canvas_height"]) == (12, 12)
    with Image.open(root / asset["normalized_path"]) as normalized:
        assert normalized.size == (12, 12)


def test_qa_retains_raw_edge_clipping_finding_after_normalization(tmp_path, monkeypatch):
    root = tmp_path
    for directory in ("metadata", "source/generated/incoming", "staging/pending/raw", "staging/pending/normalized", "previews/contact_sheets"):
        (root / directory).mkdir(parents=True, exist_ok=True)
    for name, path in {
        "ROOT": root, "MANIFEST_PATH": root / "metadata/manifest.json", "CATALOG_PATH": root / "metadata/catalog.csv",
        "QA_JSON_PATH": root / "metadata/qa_report.json", "QA_MD_PATH": root / "metadata/qa_report.md",
        "QA_CSV_PATH": root / "metadata/qa_report.csv", "CONTACT_SHEET_PATH": root / "previews/contact_sheets/pilot_pending.png",
    }.items():
        monkeypatch.setattr(core, name, path)
    image = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
    ImageDraw.Draw(image).rectangle((0, 2, 4, 6), fill=(104, 162, 154, 255))
    image.save(root / "source/generated/incoming/clipped.png")
    batch = {"assets": [{"source": "source/generated/incoming/clipped.png", "category": "icu", "asset_type": "patient_monitor_floor"}]}
    (root / "metadata/pilot_batch.json").write_text(json.dumps(batch), encoding="utf-8")
    core.ingest_batch("metadata/pilot_batch.json")
    core.normalize_pending()
    report = core.run_qa()
    assert report["assets"][0]["status"] == "warning"
    assert "touching_canvas_edge" in {issue["code"] for issue in report["assets"][0]["issues"]}
    try:
        core.approve_assets(["patient_monitor_floor_01"])
    except ValueError as error:
        assert "human QA disposition" in str(error)
    else:
        raise AssertionError("warning status must require an explicit human disposition")
    assert core.approve_assets(
        ["patient_monitor_floor_01"], human_qa_disposition="Human review confirmed this source-edge cue is benign."
    ) == ["patient_monitor_floor_01"]
    approved = core.load_manifest()["assets"][0]
    assert approved["approval_status"] == "approved"
    assert approved["human_qa_disposition"] == "Human review confirmed this source-edge cue is benign."


def test_grid_locked_components_remain_part_of_one_logical_manifest_asset(tmp_path, monkeypatch):
    root = tmp_path
    for directory in ("metadata", "source/generated/incoming", "staging/pending/raw", "staging/pending/normalized"):
        (root / directory).mkdir(parents=True, exist_ok=True)
    for name, path in {
        "ROOT": root, "MANIFEST_PATH": root / "metadata/manifest.json", "CATALOG_PATH": root / "metadata/catalog.csv",
        "QA_JSON_PATH": root / "metadata/qa_report.json", "QA_MD_PATH": root / "metadata/qa_report.md",
        "QA_CSV_PATH": root / "metadata/qa_report.csv",
    }.items():
        monkeypatch.setattr(core, name, path)

    source = Image.new("RGBA", (16, 16), (40, 55, 70, 255))
    source.save(root / "source/generated/incoming/door.png")
    leaf = Image.new("RGBA", (16, 8), (0, 0, 0, 0))
    for y in range(8):
        for x in range(16):
            leaf.putpixel((x, y), (0, 0, 0, 0) if x < 8 else (140, 180, 194, 255))
    leaf.save(root / "source/generated/incoming/leaf.png")
    batch = {"assets": [{
        "source": "source/generated/incoming/door.png", "crop": [0, 0, 16, 16], "category": "architecture",
        "asset_type": "test_architecture_door", "source_scale": 8, "expected_native_dimensions": [2, 2],
        "normalization_mode": "architecture_grid_preserving", "anchor": "wall_center",
        "components": [{
            "role": "leaf_projection", "filename": "test_architecture_door_leaf_projection_01.png",
            "source": "source/generated/incoming/leaf.png", "crop": [0, 0, 16, 8], "expected_native_dimensions": [2, 1],
            "anchor_relative_to_logical_native": [0, 1], "alpha_policy": "masked_overlay",
        }],
    }]}
    (root / "metadata/pilot_batch.json").write_text(json.dumps(batch), encoding="utf-8")

    assert len(core.ingest_batch("metadata/pilot_batch.json")) == 1
    assert core.normalize_pending() == ["test_architecture_door_01"]
    report = core.run_qa()
    manifest = core.load_manifest()
    assert len(manifest["assets"]) == 1
    asset = manifest["assets"][0]
    # This synthetic 2x1 overlay is intentionally below the generic size cue;
    # the important behavior is that it stays a non-failing child of one asset.
    assert asset["qa_status"] in {"pass", "warning"}
    assert asset["components"][0]["qa_status"] in {"pass", "warning"}
    assert asset["components"][0]["anchor_relative_to_logical_native"] == [0, 1]
    assert (root / asset["components"][0]["normalized_path"]).is_file()
    core.write_catalog()
    rows = (root / "metadata/catalog.csv").read_text(encoding="utf-8").splitlines()
    assert len(rows) == 2
    assert "component_count" in rows[0]
    assert report["assets_checked"] == 1
    core.approve_assets(["test_architecture_door_01"], human_qa_disposition="Synthetic small overlay is an intentional test fixture.")
    approved = core.load_manifest()["assets"][0]
    assert (root / approved["components"][0]["approved_staging_path"]).is_file()
    assert (root / approved["components"][0]["final_path"]).is_file()
