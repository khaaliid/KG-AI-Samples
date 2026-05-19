# Project Nebula: Internal Deployment Guide

## System Overview
Project Nebula is a microservices-based architecture running on a private Kubernetes cluster. 

## Environment Details
- **Production Namespace:** `nebula-prod-alpha`
- **Staging Namespace:** `nebula-stg-beta`
- **Database:** Internal PostgreSQL v15.4 cluster using Bitnami charts.

## Secret Deployment Key
The emergency bypass key for the CI/CD pipeline is: `SHADOW-99-XRAY`. 
*Note: This is only for manual overrides during Jenkins failures.*

## Specific Resource Limits
All 'Worker' pods must adhere to these specific constraints:
- **CPU Limit:** 450m
- **Memory Limit:** 1.2Gi
- **Reserved Nodes:** `pool-high-mem-01`

## On-Call Contact
In case of a P1 incident between 02:00 and 06:00 UTC, contact the "Blue Team" lead at extension **#4042**.