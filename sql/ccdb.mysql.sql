-- MySQL Script generated by MySQL Workbench
-- Thu Apr 15 01:21:55 2021
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema ccdb
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema ccdb
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `ccdb` DEFAULT CHARACTER SET latin1 ;
USE `ccdb` ;

-- -----------------------------------------------------
-- Table `ccdb`.`runRanges`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ccdb`.`runRanges` ;

CREATE TABLE IF NOT EXISTS `ccdb`.`runRanges` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `created` TIMESTAMP NOT NULL DEFAULT 20070101000000,
  `modified` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `name` VARCHAR(45) NULL DEFAULT '',
  `runMin` INT NOT NULL,
  `runMax` INT NOT NULL,
  `comment` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  INDEX `run search` (`runMin` ASC, `runMax` ASC) VISIBLE)
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `ccdb`.`variations`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ccdb`.`variations` ;

CREATE TABLE IF NOT EXISTS `ccdb`.`variations` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `created` TIMESTAMP NOT NULL DEFAULT 20070101000000,
  `modified` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `name` VARCHAR(100) NOT NULL DEFAULT 'default',
  `description` VARCHAR(255) NULL,
  `authorId` INT NOT NULL DEFAULT 1,
  `comment` TEXT NULL DEFAULT NULL,
  `parentId` INT NOT NULL DEFAULT 1,
  `isLocked` TINYINT(1) NOT NULL DEFAULT 0,
  `lockTime` TIMESTAMP NULL DEFAULT NULL,
  `lockAuthorId` INT NULL DEFAULT NULL,
  `goBackBehavior` INT NOT NULL DEFAULT 0,
  `goBackTime` TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  INDEX `name_search` USING HASH (`name`) VISIBLE,
  INDEX `fk_variations_variations1_idx` (`parentId` ASC) VISIBLE)
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `ccdb`.`eventRanges`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ccdb`.`eventRanges` ;

CREATE TABLE IF NOT EXISTS `ccdb`.`eventRanges` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `modified` TIMESTAMP NOT NULL DEFAULT 20070101000000,
  `runNumber` INT NOT NULL,
  `eventMin` INT NOT NULL,
  `eventMax` INT NOT NULL,
  `comment` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `ideventRanges_UNIQUE` (`id` ASC) VISIBLE)
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `ccdb`.`directories`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ccdb`.`directories` ;

CREATE TABLE IF NOT EXISTS `ccdb`.`directories` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `modified` TIMESTAMP NOT NULL DEFAULT 20070101000000,
  `name` VARCHAR(255) NOT NULL DEFAULT '',
  `parentId` INT NOT NULL DEFAULT 0,
  `authorId` INT NOT NULL DEFAULT 1,
  `comment` TEXT NULL DEFAULT NULL,
  `isDeprecated` TINYINT(1) NOT NULL DEFAULT 0,
  `deprecatedById` INT NOT NULL DEFAULT -1,
  PRIMARY KEY (`id`),
  INDEX `fk_directories_directories1_idx` (`parentId` ASC) VISIBLE,
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE)
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `ccdb`.`typeTables`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ccdb`.`typeTables` ;

CREATE TABLE IF NOT EXISTS `ccdb`.`typeTables` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `modified` TIMESTAMP NOT NULL DEFAULT 20070101000000,
  `directoryId` INT NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `nRows` INT NOT NULL DEFAULT 1,
  `nColumns` INT NOT NULL,
  `nAssignments` INT NOT NULL DEFAULT 0,
  `authorId` INT NOT NULL DEFAULT 1,
  `comment` TEXT NULL DEFAULT NULL,
  `isDeprecated` TINYINT(1) NOT NULL DEFAULT 0,
  `deprecatedById` INT NOT NULL DEFAULT -1,
  `isLocked` TINYINT(1) NOT NULL DEFAULT 0,
  `lockAuthorId` INT NULL DEFAULT NULL,
  `lockTime` TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  INDEX `fk_constantTypes_directories1_idx` (`directoryId` ASC) VISIBLE)
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `ccdb`.`constantSets`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ccdb`.`constantSets` ;

CREATE TABLE IF NOT EXISTS `ccdb`.`constantSets` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `modified` TIMESTAMP NOT NULL DEFAULT 20070101000000,
  `vault` LONGTEXT NOT NULL,
  `constantTypeId` INT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  INDEX `fk_constantSets_constantTypes1_idx` (`constantTypeId` ASC) VISIBLE)
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `ccdb`.`assignments`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ccdb`.`assignments` ;

CREATE TABLE IF NOT EXISTS `ccdb`.`assignments` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `modified` TIMESTAMP NOT NULL DEFAULT 20070101000000,
  `variationId` INT NOT NULL,
  `runRangeId` INT NULL,
  `eventRangeId` INT NULL,
  `authorId` INT NOT NULL DEFAULT 1,
  `comment` TEXT NULL,
  `constantSetId` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_assignments_variations1_idx` (`variationId` ASC) VISIBLE,
  INDEX `fk_assignments_runRanges1_idx` (`runRangeId` ASC) VISIBLE,
  INDEX `fk_assignments_eventRanges1_idx` (`eventRangeId` ASC) VISIBLE,
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  INDEX `date_sort_index` USING BTREE (`created`) VISIBLE,
  INDEX `fk_assignments_constantSets1_idx` (`constantSetId` ASC) VISIBLE)
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `ccdb`.`columns`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ccdb`.`columns` ;

CREATE TABLE IF NOT EXISTS `ccdb`.`columns` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `modified` TIMESTAMP NOT NULL DEFAULT 20070101000000,
  `name` VARCHAR(45) NOT NULL,
  `typeId` INT NOT NULL,
  `columnType` ENUM('int', 'uint','long','ulong','double','string','bool') NULL,
  `order` INT NOT NULL,
  `comment` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  INDEX `fk_columns_constantTypes1_idx` (`typeId` ASC) VISIBLE)
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `ccdb`.`tags`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ccdb`.`tags` ;

CREATE TABLE IF NOT EXISTS `ccdb`.`tags` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE)
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `ccdb`.`variations_has_tags`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ccdb`.`variations_has_tags` ;

CREATE TABLE IF NOT EXISTS `ccdb`.`variations_has_tags` (
  `variations_id` INT NOT NULL,
  `tags_id` INT NOT NULL,
  PRIMARY KEY (`variations_id`, `tags_id`),
  INDEX `fk_variations_has_tags_tags1_idx` (`tags_id` ASC) VISIBLE)
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `ccdb`.`users`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ccdb`.`users` ;

CREATE TABLE IF NOT EXISTS `ccdb`.`users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `lastActionTime` TIMESTAMP NOT NULL DEFAULT 00010101000000,
  `name` VARCHAR(100) NOT NULL,
  `password` VARCHAR(100) NULL,
  `roles` TEXT NOT NULL,
  `info` VARCHAR(125) NOT NULL,
  `isDeleted` TINYINT(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE)
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `ccdb`.`logs`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ccdb`.`logs` ;

CREATE TABLE IF NOT EXISTS `ccdb`.`logs` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `affectedIds` TEXT NOT NULL,
  `action` VARCHAR(7) NOT NULL,
  `description` VARCHAR(255) NOT NULL,
  `comment` TEXT NULL,
  `authorId` INT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  INDEX `fk_logs_users1_idx` (`authorId` ASC) VISIBLE)
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `ccdb`.`schemaVersions`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ccdb`.`schemaVersions` ;

CREATE TABLE IF NOT EXISTS `ccdb`.`schemaVersions` (
  `id` INT NOT NULL,
  `schemaVersion` INT NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ccdb`.`user`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ccdb`.`user` ;

CREATE TABLE IF NOT EXISTS `ccdb`.`user` (
  `username` VARCHAR(16) NOT NULL,
  `email` VARCHAR(255) NULL,
  `password` VARCHAR(32) NOT NULL,
  `create_time` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP);


-- -----------------------------------------------------
-- Table `ccdb`.`assignmentsMaterializedView`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ccdb`.`assignmentsMaterializedView` ;

CREATE TABLE IF NOT EXISTS `ccdb`.`assignmentsMaterializedView` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `assignmentsId` INT NOT NULL,
  `variationsId` INT NOT NULL,
  `constantSetsId` INT NOT NULL,
  `typeTablesId` INT NOT NULL,
  `runRangesId` INT NOT NULL,
  `runMin` INT NOT NULL,
  `runMax` INT NOT NULL,
  `assignmentTime` TIMESTAMP NOT NULL,
  INDEX `fk_assignmentsMaterializedView_assignments1_idx` (`assignmentsId` ASC) VISIBLE,
  INDEX `fk_assignmentsMaterializedView_variations1_idx` (`variationsId` ASC) VISIBLE,
  INDEX `fk_assignmentsMaterializedView_constantSets1_idx` (`constantSetsId` ASC) VISIBLE,
  INDEX `fk_assignmentsMaterializedView_typeTables1_idx` (`typeTablesId` ASC) VISIBLE,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  INDEX `fk_assignmentsMaterializedView_runRanges1_idx` (`runRangesId` ASC) VISIBLE,
  CONSTRAINT `fk_assignmentsMaterializedView_assignments1`
    FOREIGN KEY (`assignmentsId`)
    REFERENCES `ccdb`.`assignments` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_assignmentsMaterializedView_variations1`
    FOREIGN KEY (`variationsId`)
    REFERENCES `ccdb`.`variations` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_assignmentsMaterializedView_constantSets1`
    FOREIGN KEY (`constantSetsId`)
    REFERENCES `ccdb`.`constantSets` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_assignmentsMaterializedView_typeTables1`
    FOREIGN KEY (`typeTablesId`)
    REFERENCES `ccdb`.`typeTables` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_assignmentsMaterializedView_runRanges1`
    FOREIGN KEY (`runRangesId`)
    REFERENCES `ccdb`.`runRanges` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
