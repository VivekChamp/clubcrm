frappe.listview_settings['Food Order Entry'] = {
	get_indicator: function(doc) {
		var colors = {
            "Cart": "red",
            "Ordered": "orange",
			"Ready": "yellow",
			"Delivered": "green",
			"Cancelled": "red"
		};
		return [__(doc.order_status), colors[doc.order_status], "order_status,=," + doc.order_status];
	}
};