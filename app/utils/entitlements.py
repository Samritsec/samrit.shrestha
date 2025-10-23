# app/utils/entitlements.py
from flask import abort
from app.models.organization import Organization
from app.models.subscription import Subscription

def get_org_and_plan(org_id: int):
    org = Organization.query.get(org_id)
    if not org:
        abort(404)
    plan = Subscription.query.get(org.subscription_id) if org.subscription_id else None
    return org, plan

def has_feature(org_id: int, feature: str) -> bool:
    _, plan = get_org_and_plan(org_id)
    feats = (plan.features or []) if plan else []
    return feature in feats

def within_user_limit(org_id: int) -> bool:
    org, plan = get_org_and_plan(org_id)
    if not plan or plan.max_users is None:
        return True  # unlimited
    current = org.total_users or 0
    return current < plan.max_users

def within_device_limit(org_id: int) -> bool:
    org, plan = get_org_and_plan(org_id)
    if not plan or plan.max_devices is None:
        return True  # unlimited
    current = org.total_devices or 0
    return current < plan.max_devices

def require_paid_active(org_id: int):
    org, _ = get_org_and_plan(org_id)
    if not org.is_paid or org.status != "active":
        abort(402)  # Payment Required / not active
