import logging

import pytest

from bitrix_.enums import DealCategory
from bitrix_.manager import BitrixManager
from starter import config


@pytest.fixture
def manager():
    webhook = config.BITRIX_REST_API
    return BitrixManager(webhook)


@pytest.mark.asyncio
async def test_get_deal_categories(manager):
    assert await manager.get_deal_categories() == []


@pytest.mark.asyncio
async def test_get_stages_for_category_ok(manager):
    assert await manager.get_stages_for_category(DealCategory.OK) == []


@pytest.mark.asyncio
async def test_get_stages_for_category_ovk(manager):
    assert await manager.get_stages_for_category(DealCategory.OVK) == []


@pytest.mark.asyncio
async def test_get_all_users(manager):
    assert await manager.get_all_users() == []


@pytest.mark.asyncio
async def test_get_deal_list(manager):
    assert await manager.get_deals_modified_last_days() == []