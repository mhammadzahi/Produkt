import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";

// Odoo reopens an action at its first view (views[0]) on every menu click.
// For the Coins app menus, reopen at the view type the user last used instead.
const STORAGE_PREFIX = "coin_product_management.last_view_type.";
const MENU_XMLID_PREFIX = "coin_product_management.";

function readViewType(actionId) {
    try {
        return browser.localStorage.getItem(STORAGE_PREFIX + actionId);
    } catch {
        return null;
    }
}

function writeViewType(actionId, viewType) {
    try {
        browser.localStorage.setItem(STORAGE_PREFIX + actionId, viewType);
    } catch {
        // storage unavailable (private mode, quota): just don't remember
    }
}

export const coinViewMemoryService = {
    dependencies: ["action", "menu"],
    start(env, { action, menu }) {
        env.bus.addEventListener("ACTION_MANAGER:UI-UPDATED", () => {
            const controller = action.currentController;
            const actionId = controller?.action?.id;
            const view = controller?.view;
            if (actionId && view?.multiRecord) {
                writeViewType(actionId, view.type);
            }
        });

        const originalSelectMenu = menu.selectMenu.bind(menu);
        menu.selectMenu = async (target) => {
            const item = typeof target === "number" ? menu.getMenu(target) : target;
            const viewType = item?.actionID && item.xmlid?.startsWith(MENU_XMLID_PREFIX)
                ? readViewType(item.actionID)
                : null;
            if (!viewType) {
                return originalSelectMenu(target);
            }
            // A stored type the action doesn't have falls back to views[0].
            await action.doAction(item.actionID, {
                clearBreadcrumbs: true,
                viewType,
                onActionReady: () => menu.setCurrentMenu(item),
            });
        };
    },
};

registry.category("services").add("coin_view_memory", coinViewMemoryService);
