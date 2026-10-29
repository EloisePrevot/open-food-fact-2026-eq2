import {
  Alert,
  Badge,
  Center,
  Code,
  Divider,
  Group,
  Loader,
  Modal,
  Stack,
  Text,
} from "@mantine/core"
import type { IngredientCandidateDto } from "@/apis/ingredients/dtos/IngredientDtos"
import { useRawData } from "@/apis/rawData/useRawData"
import { HttpError } from "@/shared/utils/http"

interface IngredientDetailModalProps {
  candidate: IngredientCandidateDto | null
  onClose: () => void
}

export function IngredientDetailModal({
  candidate,
  onClose,
}: IngredientDetailModalProps) {
  const identifiant = candidate?.identifiant ?? null
  const { data: rawData, isLoading, isError, error } = useRawData(identifiant)

  return (
    <Modal
      onClose={onClose}
      opened={candidate !== null}
      size="lg"
      title={candidate?.nomProduit}
    >
      {candidate !== null && (
        <Stack gap="sm">
          <Group gap="sm">
            <Badge
              color={candidate.produitDeBase ? "teal" : "blue"}
              variant="light"
            >
              {candidate.produitDeBase
                ? "Produit de base"
                : "Produit de marque"}
            </Badge>
            <Text c="dimmed" size="sm">
              Similarité {candidate.score.toFixed(2)}
            </Text>
          </Group>
          <Text c="dimmed" size="sm">
            Identifiant : {candidate.identifiant}
          </Text>

          <Divider label="Données brutes" labelPosition="left" />

          {isLoading && (
            <Center py="md">
              <Loader />
            </Center>
          )}
          {isError &&
            (error instanceof HttpError && error.status === 404 ? (
              <Text c="dimmed" size="sm">
                Données brutes non disponibles pour ce produit.
              </Text>
            ) : (
              <Alert
                color="red"
                title="Chargement des données brutes impossible"
              >
                {error instanceof Error ? error.message : "Erreur inconnue"}
              </Alert>
            ))}
          {rawData && (
            <Stack gap="xs">
              <Text size="sm">Source : {rawData.source}</Text>
              <Text size="sm">Date d'ingestion : {rawData.dateIngestion}</Text>
              <Code block>{JSON.stringify(rawData.chargeUtile, null, 2)}</Code>
            </Stack>
          )}
        </Stack>
      )}
    </Modal>
  )
}
