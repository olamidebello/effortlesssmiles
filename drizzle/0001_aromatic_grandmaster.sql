ALTER TABLE `orders` ADD `payment_slot` text;--> statement-breakpoint
CREATE UNIQUE INDEX `orders_payment_slot_unique` ON `orders` (`payment_slot`);