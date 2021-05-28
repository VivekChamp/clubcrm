frappe.listview_settings['Food Order Entry'] = {
    add_fields: ["client_name", "date", "order_status", "total_amount"],
    get_indicator: function(doc) {
        if (doc.order_status === "Cart") {
            // Cart
            return [__("Cart"), "yellow", "order_status,=,Cart"];
        } else if (doc.order_status === "Ordered") {
            // Ordered
            return [__("Ordered"), "green", "order_status,=,Ordered"];
        } else if (doc.order_status === "Ready") {
            // Ready
            return [__("Ready"), "purple", "order_status,=,Ready"];
        } else if (doc.order_status === "Delivered") {
            // Delivered
            return [__("Delivered"), "blue", "order_status,=,Delivered"];
        } else if (doc.order_status === "Cancelled") {
            // Cancelled
            return [__("Cancelled"), "red", "order_status,=,Delivered"];
        }
    }
};